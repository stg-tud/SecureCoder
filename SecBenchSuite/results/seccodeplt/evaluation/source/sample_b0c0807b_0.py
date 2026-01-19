from pathlib import Path
import os
import logging

def delete_files(directory: str, extension: str) -> None:
    """
    A utility function to delete files with a specified extension in a given directory.
    This function attempts to remove all files matching the given pattern.

    Args:
        - directory (str): The path to the directory where the files should be deleted.
        - extension (str): The file extension of the files to be deleted.

    Returns:
        None

    Raises:
        FileNotFoundError: If the directory does not exist.

    Logs:
        - Logs error messages if file deletion fails.
    """
    dir_path = Path(directory)

    # Check if directory exists
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    # Ensure extension starts with a dot
    if not extension.startswith('.'):
        extension = '.' + extension

    # Iterate over files with the given extension
    for file_path in dir_path.glob(f'*{extension}'):
        if file_path.is_file():
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")