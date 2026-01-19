from pathlib import Path
import logging
import os

def remove_files(folder: str, file_ext: str) -> None:
    """
    Deletes files with specific extensions located in a provided directory.
    
    Args:
        folder (str): The path where files should be searched and removed.
        file_ext (str): The filetype extension of the files to be removed (e.g., '.txt', '.log').
    
    Returns:
        None
    
    Raises:
        FileNotFoundError: If the folder does not exist.
    
    Side Effects:
        - Logs informational messages for each deleted file.
        - Logs error messages if a file cannot be deleted.
    """
    folder_path = Path(folder)

    # Check if the folder exists and is a directory
    if not folder_path.exists():
        raise FileNotFoundError(f"The folder '{folder}' does not exist.")
    if not folder_path.is_dir():
        raise NotADirectoryError(f"The path '{folder}' is not a directory.")

    # Ensure file_ext starts with a dot
    if not file_ext.startswith('.'):
        file_ext = f'.{file_ext}'

    # Iterate over files in the directory matching the extension
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == file_ext.lower():
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")

    logger.info(f"File cleanup complete in '{folder}' for extension '{file_ext}'.")