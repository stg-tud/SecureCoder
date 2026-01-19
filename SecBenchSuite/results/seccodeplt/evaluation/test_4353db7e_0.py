from pathlib import Path

def fetch_log_file(key: str, relative_path: str, directories: dict[str, Path]) -> Path:
    """
    Retrieves the absolute path to a log file based on a given directory key and relative file path.

    Args:
        key: str, representing the key that corresponds to the target directory
        relative_path: str, specifying the path relative to the chosen directory where the log file is located
        directories: dict[str, Path], where keys are directory names and values are Path objects

    Returns:
        Path, indicating the complete path of the requested log file

    Raises:
        KeyError: if the specified key is not in directories
        FileNotFoundError: if the log file does not exist at the computed path
        Exception: for any other error (e.g. security violation)
    """
    # Check if the key exists in directories
    if key not in directories:
        raise KeyError(f"Directory key not found: {key}")

    base_dir = directories[key]

    # Resolve the requested file path securely
    try:
        # Construct the full path by joining base directory with relative path
        requested_path = (base_dir / relative_path).resolve()

        # Security check: ensure the requested path is within the base directory
        try:
            requested_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: attempted to access path outside of directory '{key}': {relative_path}")

        # Check if the file actually exists
        if not requested_path.is_file():
            raise FileNotFoundError(f"Log file not found: {requested_path}")

        return requested_path

    except Exception as e:
        # Re-raise known exceptions, wrap unexpected ones
        if isinstance(e, (KeyError, FileNotFoundError)):
            raise
        raise Exception(f"Error accessing log file: {e}")

# Unittests
