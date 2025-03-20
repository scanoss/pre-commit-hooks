import logging
import subprocess
from pathlib import Path

DEFAULT_RESULTS_PATH = ".scanoss/results.json"


def set_bom_settings(scan_cmd: list[str], settings_file: str, sbom_file: str) -> None:
    """Set the BOM settings file for the scan command if it exists."""

    identify = None

    settings_file_path = Path(settings_file).resolve()
    legacy_sbom_file_path = Path(sbom_file).resolve()

    # Prefer settings file over legacy sbom file
    if settings_file_path.is_file():
        identify = str(settings_file_path)
        scan_cmd.extend(["--settings", identify])
    elif legacy_sbom_file_path.is_file():
        identify = str(legacy_sbom_file_path)
        scan_cmd.extend(["--identify", identify, "-F", "512"])


def maybe_setup_results_dir(results_dir: str):
    """Create the results directory if it does not exist."""
    results_dir_path = Path(results_dir)
    results_dir_path.mkdir(exist_ok=True)


def maybe_remove_old_results(results_path: str):
    """Remove the old results file if it exists."""
    results_file = Path(results_path)
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
