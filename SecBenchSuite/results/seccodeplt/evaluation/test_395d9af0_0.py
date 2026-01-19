from pathlib import Path
import logging
import os

def purge_files(dir_path: str, ext_type: str) -> None:
    """
    Removes files with a particular file extension in a specified directory.
    
    Args:
        dir_path (str): The location from which the files with the provided extension will be deleted.
        ext_type (str): The file extension that determines the type of the files to remove.
    
    Raises:
        FileNotFoundError: If the given directory does not exist.
    
    Returns:
        None
    """
    directory = Path(dir_path)
    
    # Check if the directory exists
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    # Ensure the path is a directory
    if not directory.is_dir():
        raise FileNotFoundError(f"Path is not a directory: {dir_path}")
    
    # Ensure extension starts with a dot
    if not ext_type.startswith('.'):
        ext_type = f'.{ext_type}'
    
    # Iterate over files with the given extension
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ext_type.lower():
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")

# Unittests
