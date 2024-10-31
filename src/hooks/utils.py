import logging
import subprocess
from pathlib import Path

DEFAULT_RESULTS_PATH = ".scanoss/results.json"


def get_identify(scan_cmd: list[str], settings_file: str, sbom_file: str) -> str | None:
    """Get the identify file path for Scanning.

    Returns:
        str | None: file path to the identify file
    """
    identify: str | None = None

    settings_file_path = Path(settings_file).resolve()
    legacy_sbom_file_path = Path(sbom_file).resolve()

    # Prefer settings file over legacy sbom file
    if settings_file_path.is_file():
        identify = str(settings_file_path)
        scan_cmd.extend(["--settings", identify])
    elif legacy_sbom_file_path.is_file():
        identify = str(legacy_sbom_file_path)
        scan_cmd.extend(["--identify", identify, "-F", "512"])

    return identify


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
