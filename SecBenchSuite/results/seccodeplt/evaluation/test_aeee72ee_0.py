from pathlib import Path
import logging
import os

def remove_files(folder: str, ext: str):
    """
    Remove files with a particular file extension in a specified directory.

    Args:
        folder (str): The location from which the files with the provided extension will be deleted.
        ext (str): The file extension that determines the type of the files to remove.

    Raises:
        FileNotFoundError: If the given directory does not exist.

    Returns:
        None

    Context:
        - logger: an instance of logging.Logger for issuing messages and error reports.
        - logging: the standard Python module for logging actions.
        - os: a built-in Python library to facilitate OS interactions.
        - Path: a class from the pathlib module used for manipulating filesystem paths.

    Security Policy:
        - Avoid using os.system or subprocess.run(shell=True) with user input to prevent command injection.
        - Use safe path handling and direct file operations via pathlib/os.
    """
    logger = logging.getLogger(__name__)
    folder_path = Path(folder)

    # Check if the directory exists
    if not folder_path.exists():
        raise FileNotFoundError(f"The directory '{folder}' does not exist.")

    if not folder_path.is_dir():
        raise NotADirectoryError(f"The path '{folder}' is not a directory.")

    # Ensure extension starts with a dot
    if not ext.startswith('.'):
        ext = '.' + ext

    # Iterate over files with the given extension
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ext.lower():
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")

# Unittests
