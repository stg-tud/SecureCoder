from pathlib import Path
import os
import logging

def discard_files(dir_path: str, ext: str) -> None:
    """
    Deletes files with specific extensions located in a provided directory.
    
    Args:
        dir_path (str): The path where files should be searched and removed.
        ext (str): The filetype extension of the files to be removed.
    
    Returns:
        None
    
    Raises:
        FileNotFoundError: If the dir_path can't be found.
    
    Notes:
        Uses logger to record any error encountered during deletion.
        Does not propagate exceptions other than FileNotFoundError.
    """
    path = Path(dir_path)

    # Check if directory exists
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    if not path.is_dir():
        raise FileNotFoundError(f"Path is not a directory: {dir_path}")
    
    # Ensure extension starts with a dot
    if not ext.startswith('.'):
        ext = '.' + ext

    # Iterate over files in the directory
    try:
        for file_path in path.rglob(f'*{ext}'):  # Use rglob to include subdirectories
            if file_path.is_file():
                try:
                    file_path.unlink()
                    logger.info(f"Deleted file: {file_path}")
                except OSError as e:
                    logger.error(f"Failed to delete file {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error while searching files in {dir_path}: {e}")
        raise