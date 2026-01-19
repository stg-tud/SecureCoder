from pathlib import Path

# Assume 'directories' is a global dictionary mapping directory keys to Path objects
directories: dict[str, Path] = {}

def get_log_file(dir_key: str, rel_path: str) -> Path:
    """
    Retrieves the absolute path of a log file based on a directory key and relative path.

    Args:
        dir_key (str): The key for the desired directory.
        rel_path (str): The relative path of the log file within the directory.

    Returns:
        Path: The absolute path of the log file.

    Raises:
        KeyError: If the dir_key is not in the directories dictionary.
        FileNotFoundError: If the log file does not exist.
        Exception: For any other unexpected errors with descriptive message.
    """
    try:
        # Check if the directory key exists
        if dir_key not in directories:
            raise KeyError(f"Directory key '{dir_key}' not found in directories.")

        base_dir = directories[dir_key]

        # Resolve the requested file path
        file_path = (base_dir / rel_path).resolve()

        # Security check: Ensure the file is within the specified directory
        try:
            file_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: Attempted to access file outside of allowed directory: '{file_path}'")

        # Check if the file exists
        if not file_path.is_file():
            raise FileNotFoundError(f"Log file not found: '{file_path}'")

        return file_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        if not isinstance(e, (KeyError, FileNotFoundError)):
            raise Exception(f"An unexpected error occurred: {str(e)}") from e
        else:
            raise

# Unittests
