###
# SPDX-License-Identifier: MIT
#
#   Copyright (c) 2024, SCANOSS
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
###
import logging
import subprocess
from pathlib import Path

DEFAULT_SCANOSS_SETTINGS_FILE = "scanoss.json"
DEFAULT_SBOM_FILE = "SBOM.json"
DEFAULT_RESULTS_DIR = ".scanoss"
DEFAULT_RESULTS_FILENAME = "results.json"
DEFAULT_RESULTS_PATH = f"{DEFAULT_RESULTS_DIR}/{DEFAULT_RESULTS_FILENAME}"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    scanoss_scan_cmd = [
        "scanoss-py",
        "scan",
        "--no-wfp-output",
        "--output",
        DEFAULT_RESULTS_PATH,
    ]

    identify = get_identify(scanoss_scan_cmd)
    if identify is None:
        log_and_exit(
            f"No SCANOSS settings file or sbom file found, please make sure you have either a {DEFAULT_SCANOSS_SETTINGS_FILE} or {DEFAULT_SBOM_FILE} file in the root of your project.",
            1,
        )

    maybe_setup_results_dir()
    maybe_remove_old_results()

    staged_files = get_staged_files()
    if not staged_files:
        log_and_exit("No files to scan. Skipping SCANOSS.", 0)

    scanoss_scan_cmd.extend(["--files", *staged_files])

    run_scan(scanoss_scan_cmd)

    present_results()

    exit(0)


def get_identify(scan_cmd: list[str]) -> str | None:
    """Get the identify file path for Scanning.

    Returns:
        str | None: file path to the identify file
    """
    identify: str | None = None

    settings_file_path = Path(DEFAULT_SCANOSS_SETTINGS_FILE).resolve()
    legacy_sbom_file_path = Path(DEFAULT_SBOM_FILE).resolve()

    # Prefer settings file over legacy sbom file
    if settings_file_path.is_file():
        identify = str(settings_file_path)
        scan_cmd.extend(["--settings", identify])
    elif legacy_sbom_file_path.is_file():
        identify = str(legacy_sbom_file_path)
        scan_cmd.extend(["--identify", identify, "-F", "512"])

    return identify


def maybe_setup_results_dir():
    """Create the results directory if it does not exist."""
    results_dir = Path(DEFAULT_RESULTS_DIR)
    results_dir.mkdir(exist_ok=True)


def maybe_remove_old_results():
    """Remove the old results file if it exists."""
    results_file = Path(DEFAULT_RESULTS_PATH)
    if results_file.is_file():
        results_file.unlink(missing_ok=True)


def log_and_exit(message: str, exit_code: int) -> None:
    """Log a message and exit with the given code.

    Args:
        message (str): message to log
        exit_code (int): exit code
    """
    if exit_code == 0:
        logging.info(message)
    else:
        logging.error(message)
    exit(exit_code)


def run_scan(scan_cmd: list[str]) -> None:
    """Run the SCANOSS scan command.

    Args:
        scan_cmd (list[str]): SCANOSS scan command
    """
    try:
        subprocess.run(scan_cmd, check=True)
    except subprocess.CalledProcessError as e:
        log_and_exit(f"Error: SCANOSS scan failed: {e}", 1)


def present_results() -> None:
    """Present the SCANOSS scan results."""
    try:
        cmd_result = subprocess.run(
            [
                "scanoss-py",
                "results",
                DEFAULT_RESULTS_PATH,
                "--has-pending",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        scan_results = cmd_result.stdout
        logging.info(scan_results)
    except subprocess.CalledProcessError as e:
        # If there are pending results, exit code is 1
        if e.returncode == 1:
            log_and_exit(
                "SCANOSS detected potential Open Source software. Please review the following:\n"
                "Run 'scanoss-lui' in the terminal to view the results in more detail.",
                1,
            )


def get_staged_files() -> list[str]:
    """Get the list of staged files in the current git repository.

    Returns:
        list[str]: list of staged files or an empty list if no files are staged.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )

        staged_files = result.stdout.strip().split("\n")
        return [f for f in staged_files if f]
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: Git command failed: {e}")
        return []
    except Exception as e:
        logging.error(f"Error: {e}")
        return []


if __name__ == "__main__":
    SystemExit(main())
