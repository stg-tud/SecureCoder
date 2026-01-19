from pathlib import Path

def fetch_log_file(dir_id: str, file_path: str, directories: dict) -> Path:
    """
    Fetches the absolute file path of a log based on a directory key and relative file path.
    Ensures the file path resides within the specified directory to prevent unauthorized access.

    Args:
        dir_id: A string that serves as the identifier for the directory.
        file_path: A string representing the relative file path inside the directory.
        directories: A dictionary mapping directory keys (type str) to their respective Path objects.

    Returns:
        The absolute path of the log file as a Path object.

    Raises:
        KeyError: If the specified directory key does not exist in the dictionary.
        FileNotFoundError: If the log file cannot be found at the provided path.
        Exception: If any unexpected error occurs, with an appropriate message.
    """
    try:
        # Check if the directory key exists
        if dir_id not in directories:
            raise KeyError(f"Directory key '{dir_id}' does not exist.")

        base_dir = directories[dir_id]

        # Resolve the target file path securely
        target_path = (base_dir / file_path).resolve()
        base_dir_resolved = base_dir.resolve()

        # Security check: Ensure the file is within the specified directory
        if not target_path.is_relative_to(base_dir_resolved):
            raise Exception(f"Access denied: File path '{file_path}' attempts to access outside the directory '{dir_id}'.")

        # Check if the file actually exists
        if not target_path.exists():
            raise FileNotFoundError(f"Log file not found: '{file_path}' in directory '{dir_id}'.")

        if not target_path.is_file():
            raise FileNotFoundError(f"Path '{file_path}' exists but is not a file.")

        return target_path

    except KeyError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        # Re-raise any other exception (including our custom ones) with appropriate message
        raise

# Unittests
