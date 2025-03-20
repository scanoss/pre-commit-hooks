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

import logging
import subprocess
from pathlib import Path


def set_bom_settings(scan_cmd: list[str], settings_file: str, sbom_file: str) -> None:
    """Set the BOM settings file for the scan command if it exists.

    Args:
        scan_cmd: scanoss-py scan command arguments list
        settings_file: settings file path
        sbom_file: SBOM file path (legacy)
    """

    settings_file_path = Path(settings_file).resolve() if settings_file is not None else None
    legacy_sbom_file_path = Path(sbom_file).resolve() if sbom_file is not None else None

    # Prefer settings file over legacy sbom file
    if settings_file_path and settings_file_path.is_file():
        scan_cmd.extend(["--settings", str(settings_file_path)])
    elif legacy_sbom_file_path and legacy_sbom_file_path.is_file():
        scan_cmd.extend(["--identify", str(legacy_sbom_file_path), "-F", "512"])  # TODO why do we need the -F 512 here?


def maybe_setup_results_dir(results_dir: str):
    """Create the results directory if it does not exist.

    Args:
        results_dir: Results directory path
    """
    if results_dir:
        results_dir_path = Path(results_dir)
        results_dir_path.mkdir(exist_ok=True)  # TODO what about exceptions?


def maybe_remove_old_results(results_path: str):
    """Remove old results directory if it exists.
    Args:
        results_path: Results file path
    """
    if results_path:
        results_file = Path(results_path)
        if results_file.is_file():
            results_file.unlink(missing_ok=True)  # TODO what about exceptions?


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


def get_staged_files() -> list[str]:
    """Get the list of staged files in the current git repository.

    Returns:
        list[str]: list of staged files or an empty list if no files are staged.
    """
    # TODO might be possible to use pre-commit git library for running git commands?
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"],
            capture_output=True,
            text=True,
            check=True,
        )
        staged_files = result.stdout.strip().split("\n")
        return [f for f in staged_files if f]
    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e}")
    except Exception as e:
        logging.error(f"{e}")
    return []
