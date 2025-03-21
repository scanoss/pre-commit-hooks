"""
SPDX-License-Identifier: MIT

  Copyright (c) 2024, SCANOSS

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
"""

import json
import logging
import subprocess

from rich.console import Console
from rich.table import Table

from .utils import (
    get_staged_files,
    log_and_exit,
    maybe_remove_old_results,
    maybe_setup_results_dir
)

# Default settings file and results location
DEFAULT_SCANOSS_SETTINGS_FILE = "scanoss.json"  # TODO remove
DEFAULT_SBOM_FILE = "SBOM.json"
DEFAULT_RESULTS_DIR = ".scanoss"
DEFAULT_RESULTS_FILENAME = "results.json"
DEFAULT_RESULTS_PATH = f"{DEFAULT_RESULTS_DIR}/{DEFAULT_RESULTS_FILENAME}"

console = Console()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_scan(scan_cmd: list[str]) -> None:
    """Run the SCANOSS scan command.

    Args:
        scan_cmd (list[str]): SCANOSS scan command
    """
    try:
        subprocess.run(scan_cmd, check=True)
    except subprocess.CalledProcessError as e:
        log_and_exit(f"SCANOSS scan failed: {e}", 1)


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
            scan_results_json = json.loads(scan_results)
            present_results_table(scan_results_json)
            exit(1)
    except Exception as e:
        log_and_exit(f"SCANOSS results command failed: {e}", 1)


def present_results_table(results: dict) -> None:
    """Present the files pending identification in a table.

    Args:
        results (dict): files pending identification
    """
    table = Table(
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Match Type")
    table.add_column("Matched")
    table.add_column("Purl")
    table.add_column("License")

    for file in results.get("results"):
        table.add_row(
            file.get("file"),
            file.get("status"),
            file.get("match_type"),
            file.get("matched"),
            file.get("purl"),
            file.get("license"),
        )
    # End for loop
    console.print(
        f"[bold red]SCANOSS detected [cyan]{results.get('total')}[/cyan] files containing potential Open Source Software:[/bold red]"
    )
    console.print(table)
    console.print(
        "Run [green]'scanoss-cc'[/green] in the terminal to view the results in more detail."
    )


def main():
    """Run the check undeclared OSS file/snippet hook

    Returns: 0 on success 1 otherwise
    """
    # Standard scanoss-py starting scan commands
    maybe_setup_results_dir(DEFAULT_RESULTS_DIR)
    maybe_remove_old_results(DEFAULT_RESULTS_PATH)
    # Get the list of pending files to be scanned
    staged_files = get_staged_files()
    if not staged_files:
        log_and_exit("No files to scan. Skipping SCANOSS.", 0)  # Nothing to do

    scanoss_scan_cmd = [
        "scanoss-py",
        "scan",
        "--no-wfp-output",
        "--output",
        DEFAULT_RESULTS_PATH,
        "--files",
        *staged_files
    ]
    # TODO add support for supplying a file-list file
    run_scan(scanoss_scan_cmd)
    present_results()
    exit(0)


if __name__ == "__main__":
    SystemExit(main())
