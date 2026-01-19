from pathlib import Path


def resolve_log_file(dir_identifier: str, file_relative_path: str, directories: dict[str, Path]) -> Path:
    """
    Retrieve the absolute path to a log file based on a directory key and a relative file path.

    Args:
        dir_identifier: str, representing the key that corresponds to the target directory
        file_relative_path: str, specifying the path relative to the chosen directory where the log file is located
        directories: dict[str, Path], where keys are directory names and values are Path objects

    Returns:
        Path: The absolute path to the requested log file

    Raises:
        KeyError: If the dir_identifier is not in directories
        FileNotFoundError: If the log file does not exist at the computed path
        Exception: For any other unexpected errors
    """
    try:
        # Retrieve the base directory using the identifier
        if dir_identifier not in directories:
            raise KeyError(f"Directory identifier '{dir_identifier}' not found in directories.")

        base_dir = directories[dir_identifier]

        # Resolve the target file path relative to the base directory
        target_path = (base_dir / file_relative_path).resolve()

        # Security check: Ensure the resolved path is within the base directory
        try:
            target_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: File '{file_relative_path}' is outside the allowed directory scope.")

        # Verify that the file actually exists
        if not target_path.is_file():
            raise FileNotFoundError(f"Log file not found: {target_path}")

        return target_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while resolving the log file: {str(e)}")