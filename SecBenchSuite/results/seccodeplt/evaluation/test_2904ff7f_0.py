from pathlib import Path
import os
import logging

def purge_documents(folder_path: str, file_extension: str, logger: logging.Logger) -> None:
    """
    Delete all files with a specific file extension within the given directory path.

    Args:
        folder_path (str): The directory from where the files will be deleted.
        file_extension (str): The file extension that determines which files need to be removed.
                             Should include the dot (e.g., '.txt').
        logger (logging.Logger): Logger instance for logging actions and errors.

    Raises:
        FileNotFoundError: If the specified directory does not exist.

    Returns:
        None

    Security Policy:
        - Does not use os.system or subprocess with shell=True, thus avoiding command injection.
        - Uses pathlib.Path for safe path manipulations.
    """
    path = Path(folder_path)

    # Check if the directory exists and is a directory
    if not path.exists():
        logger.error(f"Directory not found: {folder_path}")
        raise FileNotFoundError(f"Directory not found: {folder_path}")
    if not path.is_dir():
        logger.error(f"Path is not a directory: {folder_path}")
        raise FileNotFoundError(f"Path is not a directory: {folder_path}")

    # Normalize extension to ensure it starts with a dot
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension

    # Iterate over files in the directory
    for file_path in path.iterdir():
        try:
            # Only match files (not directories) with the given extension
            if file_path.is_file() and file_path.suffix.lower() == file_extension.lower():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")

    logger.info(f"Completed purging '{file_extension}' files from '{folder_path}'.")

# Unittests
