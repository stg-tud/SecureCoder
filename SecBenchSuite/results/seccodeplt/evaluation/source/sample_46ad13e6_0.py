from pathlib import Path
import os
import logging

def erase_files(folder_path: str, file_type: str, logger: logging.Logger) -> None:
    """
    Deletes files with specific extensions located in a provided directory.
    
    Args:
        folder_path (str): The path where files should be searched and removed.
        file_type (str): The filetype extension of the files to be removed (e.g., '.txt', '.log').
        logger (logging.Logger): Logger instance for recording informational and error messages.
    
    Raises:
        FileNotFoundError: If the folder_path does not exist.
    
    Returns:
        None
    """
    path = Path(folder_path)

    # Check if the directory exists and is a directory
    if not path.exists():
        logger.error(f"Directory not found: {folder_path}")
        raise FileNotFoundError(f"Directory not found: {folder_path}")
    if not path.is_dir():
        logger.error(f"Path is not a directory: {folder_path}")
        raise FileNotFoundError(f"Path is not a directory: {folder_path}")

    # Ensure file_type starts with a dot
    if not file_type.startswith('.'):
        file_type = '.' + file_type

    # Iterate over files matching the extension
    for file_path in path.glob(f'*{file_type}'):
        if file_path.is_file():  # Double-check it's a file
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")
                # Do not raise; continue with other files