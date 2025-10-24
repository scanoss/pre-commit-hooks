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

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table

DEFAULT_SCANOSS_SCAN_RESULTS_FILE = Path(".scanoss") / "results.json"

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

console = Console()


def configure_logging(debug: bool) -> None:
    """
    Configure global logging level based on the --debug flag.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT, force=True)
    logging.getLogger("scanoss").setLevel(log_level)
    logging.debug("Debug mode enabled")


def get_staged_files() -> list[str]:
    """Get the list of staged files in the current git repository.

    Returns:
        list[str]: list of staged files or an empty list if no files are staged.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--name-only", "--diff-filter=ACMR"],
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


def run_subcommand(
    command: list[str], check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a command safely and return the completed process.

    Args:
        command (list[str]): Command to run
        check (bool): Whether to check the return code of the command
    """
    return subprocess.run(command, check=check, capture_output=True, text=True)


def sanitize_scan_command(command: List[str]) -> List[str]:
    """
    Return a copy with sensitive flag values redacted.

    Args:
        command (List[str]): The command arguments to sanitize.

    Returns:
        List[str]: The sanitized command arguments.
    """
    SENSITIVE_FLAGS = {"--key", "--proxy"}  # proxy may embed creds

    sanitized = command.copy()

    for i, arg in enumerate(command):
        for flag in SENSITIVE_FLAGS:
            if arg == flag:
                if i + 1 < len(sanitized):
                    sanitized[i + 1] = "*****"
            elif arg.startswith(f"{flag}="):
                sanitized[i] = f"{flag}=*****"
    return sanitized


def present_results_table(results: dict, output_path: Path) -> None:
    """Present the files pending identification in a table.

    Args:
        results (dict): files pending identification
        output_path (Path): path to the output file containing scan results
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

    for file in results.get("results", []):
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

    # Determine the appropriate command to show based on whether a custom output path was used
    if output_path == DEFAULT_SCANOSS_SCAN_RESULTS_FILE:
        command_msg = "Run [green]'scanoss-cc'[/green] in the terminal to view the results in more detail."
    else:
        command_msg = f"Run [green]'scanoss-cc --input {output_path}'[/green] in the terminal to view the results in more detail."

    console.print(command_msg)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--api-url",
    type=click.STRING,
    envvar="SCANOSS_SCAN_URL",
    help="SCANOSS API URL (can also be set via environment variable SCANOSS_SCAN_URL).",
)
@click.option(
    "--api-key",
    type=click.STRING,
    envvar="SCANOSS_API_KEY",
    help="SCANOSS API key (can also be set via environment variable SCANOSS_API_KEY).",
)
@click.option(
    "--proxy",
    type=click.STRING,
    envvar="HTTPS_PROXY",
    help="Proxy URL to use for connections (optional). "
    'Can also use the environment variable "HTTPS_PROXY=<ip>:<port>" '
    'and "grcp_proxy=<ip>:<port>" for gRPC',
)
@click.option(
    "--pac",
    type=click.STRING,
    help='Proxy auto configuration (optional). Specify a file, http url or "auto" to try to discover it.',
)
@click.option(
    "--ca-cert",
    type=click.STRING,
    envvar=["REQUESTS_CA_BUNDLE", "GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"],
    help="Alternative certificate PEM file (optional). "
    "Can also use the environment variable "
    '"REQUESTS_CA_BUNDLE=/path/to/cacert.pem" and '
    '"GRPC_DEFAULT_SSL_ROOTS_FILE_PATH=/path/to/cacert.pem" for gRPC',
)
@click.option("--ignore-cert-errors", is_flag=True, help="Ignore certificate errors")
@click.option("--rest", is_flag=True, help="Use REST instead of gRPC")
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=DEFAULT_SCANOSS_SCAN_RESULTS_FILE,
    help=f"Output file for scan results (default: {DEFAULT_SCANOSS_SCAN_RESULTS_FILE})",
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    default=os.environ.get("SCANOSS_DEBUG", "").lower() == "true",
    help="Enable debug messages (can also be set via environment variable SCANOSS_DEBUG).",
)
@click.pass_context
def main(
    ctx: click.Context,
    api_url: str | None,
    api_key: str | None,
    proxy: str | None,
    pac: str | None,
    ca_cert: str | None,
    ignore_cert_errors: bool,
    rest: bool,
    output: Path,
    debug: bool,
) -> None:
    """Check for potential undeclared open source software in staged files.

    This pre-commit hook scans staged files using SCANOSS to detect undeclared open source code.
    """
    # TODO: Warn users if .scanoss is not in .gitignore
    configure_logging(debug)

    # Get the list of pending files to be scanned
    staged_files = get_staged_files()
    if not staged_files:
        logging.info("No files to scan. Skipping SCANOSS")
        ctx.exit(EXIT_SUCCESS)

    logging.debug(f"Staged files to scan: {staged_files}")

    scanoss_scan_cmd = [
        "scanoss-py",
        "scan",
        "--no-wfp-output",
        "--files",
        *staged_files,
    ]

    if api_url is not None:
        scanoss_scan_cmd.extend(["--apiurl", api_url])

    if api_key is not None:
        scanoss_scan_cmd.extend(["--key", api_key])

    if proxy is not None:
        scanoss_scan_cmd.extend(["--proxy", proxy])

    if pac is not None:
        scanoss_scan_cmd.extend(["--pac", pac])

    if ca_cert is not None:
        scanoss_scan_cmd.extend(["--ca-cert", ca_cert])

    if debug:
        scanoss_scan_cmd.append("--debug")

    if ignore_cert_errors:
        scanoss_scan_cmd.append("--ignore-cert-errors")

    if rest:
        scanoss_scan_cmd.append("--rest")

    process_status = console.status("[bold green] Running SCANOSS scan...")
    logging.debug(f"Executing command: {sanitize_scan_command(scanoss_scan_cmd)}")

    process_status.start()

    try:
        scan_result = run_subcommand(scanoss_scan_cmd)
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Error running scanoss command with return code {e.returncode}: {e.stderr}"
        )
        ctx.exit(EXIT_FAILURE)

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Ensuring output directory exists: {output.parent}")
    except OSError as e:
        logging.error(f"Failed to create output directory {output.parent}: {e}")
        process_status.stop()
        ctx.exit(EXIT_FAILURE)

    try:
        with open(output, "w") as output_file:
            output_file.write(scan_result.stdout)
        logging.debug(f"Scan results saved to {output}")
    except OSError as e:
        logging.error(f"Failed to write scan results to {output}: {e}")
        process_status.stop()
        ctx.exit(EXIT_FAILURE)

    scanoss_has_pending_command = [
        "scanoss-py",
        "results",
        str(output),
        "--has-pending",
        "--format",
        "json",
    ]

    process_status.update("[bold green] Checking for pending results...")

    has_pending_results = run_subcommand(scanoss_has_pending_command, check=False)
    if has_pending_results.returncode == 1:
        try:
            payload = json.loads(has_pending_results.stdout)
            process_status.stop()
            present_results_table(payload, output)
            ctx.exit(EXIT_FAILURE)
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON response from SCANOSS")
            ctx.exit(EXIT_FAILURE)
    if has_pending_results.returncode != 0:
        logging.error(
            f"SCANOSS 'results' command failed with exit code {has_pending_results.returncode}: {has_pending_results.stderr}"
        )
        ctx.exit(has_pending_results.returncode)

    process_status.stop()
    console.print("[bold green] ✅ No pending results found. It's safe to commit.")
    ctx.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
