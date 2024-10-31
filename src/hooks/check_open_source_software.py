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

import subprocess
import sys
from pathlib import Path

DEFAULT_SCANOSS_SETTINGS_FILE = "scanoss.json"
DEFAULT_SBOM_FILE = "SBOM.json"
DEFAULT_RESULTS_DIR = ".scanoss"
DEFAULT_RESULTS_FILENAME = "results.json"
DEFAULT_RESULTS_PATH = f"{DEFAULT_RESULTS_DIR}/{DEFAULT_RESULTS_FILENAME}"


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
        print_stderr(
            f"No SCANOSS settings file or sbom file found, please make sure you have either a {DEFAULT_SCANOSS_SETTINGS_FILE} or {DEFAULT_SBOM_FILE} file in the root of your project.",
        )
        exit(1)

    maybe_setup_results_dir()
    maybe_remove_old_results()

    staged_files = get_staged_files()
    if not staged_files:
        print_stderr(
            "No files to scan. Skipping SCANOSS.",
        )
        exit(0)

    scanoss_scan_cmd.extend(
        [
            "--files",
            *staged_files,
        ]
    )

    # Run the scan
    try:
        subprocess.run(scanoss_scan_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print_stderr(
            f"Error: SCANOSS scan failed: {e}",
        )
        exit(1)

    # Present the results
    scan_results = None
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
            check=True,
        )

        scan_results = cmd_result.stdout
    except subprocess.CalledProcessError as e:
        # If there are pending results, exit code is 1
        if e.returncode == 1:
            print_stderr(
                "SCANOSS detected potential Open Source software. Please review the following:",
            )
            print_stderr(
                "Run 'scanoss-lui' in the terminal to view the results in more detail.",
            )
            print_stderr(scan_results)
            exit(1)
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
    results_dir = Path(".scanoss")
    results_dir.mkdir(exist_ok=True)


def maybe_remove_old_results():
    """Remove the old results file if it exists."""
    results_file = Path(DEFAULT_RESULTS_PATH)
    if results_file.is_file():
        results_file.unlink(missing_ok=True)


def print_stderr(message: str) -> None:
    """Print a message to stderr.

    Args:
        message (str): message to print to stderr
    """
    print(message, file=sys.stderr)


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

        staged_files = [f for f in staged_files if f]

        return staged_files
    except subprocess.CalledProcessError as e:
        print_stderr(f"Error: Git command failed: {e}")
        return []
    except Exception as e:
        print_stderr(f"Error: {e}")
        return []


if __name__ == "__main__":
    SystemExit(main())
