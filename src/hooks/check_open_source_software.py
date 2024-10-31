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

from utils import (
    get_identify,
    get_staged_files,
    log_and_exit,
    maybe_remove_old_results,
    maybe_setup_results_dir,
)

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

    identify = get_identify(
        scanoss_scan_cmd, DEFAULT_SCANOSS_SETTINGS_FILE, DEFAULT_SBOM_FILE
    )
    if identify is None:
        log_and_exit(
            f"No SCANOSS settings file or sbom file found, please make sure you have either a {DEFAULT_SCANOSS_SETTINGS_FILE} or {DEFAULT_SBOM_FILE} file in the root of your project.",
            1,
        )

    maybe_setup_results_dir(DEFAULT_RESULTS_DIR)
    maybe_remove_old_results(DEFAULT_RESULTS_PATH)

    staged_files = get_staged_files()
    if not staged_files:
        log_and_exit("No files to scan. Skipping SCANOSS.", 0)

    scanoss_scan_cmd.extend(["--files", *staged_files])

    run_scan(scanoss_scan_cmd)

    present_results()

    exit(0)


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
        )

        scan_results = cmd_result.stdout

        # If the return code is 1, SCANOSS detected pending potential Open Source software that needs to be reviewed.
        if cmd_result.returncode == 1:
            logging.info(
                "SCANOSS detected potential Open Source software. Please review the following:"
            )
            logging.info(scan_results, 1)
            log_and_exit(
                "Run 'scanoss-lui' in the terminal to view the results in more detail.",
                1,
            )
    except Exception as e:
        log_and_exit(f"Error: SCANOSS results command failed: {e}", 1)


if __name__ == "__main__":
    SystemExit(main())
