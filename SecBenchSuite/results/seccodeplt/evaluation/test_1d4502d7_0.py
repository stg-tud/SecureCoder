from pathlib import Path

def retrieve_log_path(log_dir: str, relative_path: str, directories: dict) -> Path:
    """
    Fetches the absolute file path of a log based on a directory key and relative file path.
    Ensures the resolved path lies within the associated directory to prevent path traversal attacks.

    Args:
        log_dir: A string that serves as the identifier for the directory.
        relative_path: A string representing the relative file path inside the directory.
        directories: A dictionary mapping directory keys (type str) to their respective Path objects.

    Returns:
        The absolute path of the log file as a Path object.

    Raises:
        KeyError: If the specified directory key does not exist in the dictionary.
        FileNotFoundError: If the log file cannot be found at the provided path.
        Exception: If any unexpected error occurs, with an appropriate message.
    """
    try:
        # Check if the log_dir exists in the directories dictionary
        if log_dir not in directories:
            raise KeyError(f"Directory key '{log_dir}' not found in directories.")

        # Get the base directory Path object
        base_dir = directories[log_dir]

        # Resolve the target file path
        file_path = (base_dir / relative_path).resolve()

        # Ensure the file_path is within the base_dir (security check against path traversal)
        try:
            file_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: '{relative_path}' attempts to access a path outside of '{log_dir}'.")

        # Check if the file exists
        if not file_path.is_file():
            raise FileNotFoundError(f"Log file not found: '{file_path}'")

        return file_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Re-raise expected exceptions, wrap others
        if not isinstance(e, (KeyError, FileNotFoundError)):
            raise Exception(f"An unexpected error occurred: {str(e)}") from e

# Unittests
