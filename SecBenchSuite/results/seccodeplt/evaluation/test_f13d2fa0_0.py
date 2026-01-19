from pathlib import Path
import os
import logging

def erase_files(dir_path: str, file_ext: str, logger: logging.Logger) -> None:
    """
    Delete all files with a specific file extension within the given directory path.

    Args:
        dir_path (str): The directory from where the files will be erased.
        file_ext (str): The file extension that determines which files need to be removed.
                        Should include the dot (e.g., '.log', '.tmp').
        logger (logging.Logger): Logger instance to log actions and errors.

    Raises:
        FileNotFoundError: If the specified directory does not exist.

    Returns:
        None

    Security Policy:
        Avoids command injection by not using os.system or subprocess with shell=True.
        Uses pathlib and os.remove with validated paths.
    """
    directory = Path(dir_path)

    # Check if directory exists and is a directory
    if not directory.exists():
        logger.error(f"Directory not found: {dir_path}")
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    if not directory.is_dir():
        logger.error(f"Path is not a directory: {dir_path}")
        raise FileNotFoundError(f"Path is not a directory: {dir_path}")

    # Ensure file_ext starts with a dot
    if not file_ext.startswith('.'):
        file_ext = '.' + file_ext

    # Iterate over files in the directory
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == file_ext.lower():
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")

# Unittests
