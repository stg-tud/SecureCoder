from pathlib import Path
import logging
import os

def clean_up_files(path_to_directory: str, file_extension: str) -> None:
    """
    Remove files with a particular file extension in a specified directory.
    
    Args:
        path_to_directory (str): The location from which the files with the provided extension will be deleted.
        file_extension (str): The file extension that determines the type of the files to remove.
    
    Raises:
        FileNotFoundError: If the given directory does not exist.
    
    Returns:
        None
    """
    directory = Path(path_to_directory)
    
    # Check if the directory exists and is indeed a directory
    if not directory.exists():
        logger.error(f"Directory not found: {path_to_directory}")
        raise FileNotFoundError(f"Directory not found: {path_to_directory}")
    
    if not directory.is_dir():
        logger.error(f"Path is not a directory: {path_to_directory}")
        raise FileNotFoundError(f"Path is not a directory: {path_to_directory}")
    
    # Ensure file_extension starts with a dot
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Iterate over files with the given extension
    for file_path in directory.glob(f'*{file_extension}'):
        if file_path.is_file():  # Ensure it's a file before attempting deletion
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")