from pathlib import Path

def remove_files(folder: str, file_type: str):
    """
    Deletes all files with the specified file extension within the given directory.

    Args:
        folder (str): The directory from where the files will be deleted.
        file_type (str): The file extension that determines which files need to be removed.
                         Should include the dot (e.g., '.txt').

    Raises:
        FileNotFoundError: If the specified directory does not exist.

    Returns:
        None
    """
    folder_path = Path(folder)

    # Check if the directory exists and is a directory
    if not folder_path.exists():
        raise FileNotFoundError(f"The directory '{folder}' does not exist.")
    if not folder_path.is_dir():
        raise FileNotFoundError(f"The path '{folder}' is not a directory.")

    # Ensure file_type starts with a dot
    if not file_type.startswith('.'):
        file_type = f'.{file_type}'

    # Iterate over files matching the extension
    for file_path in folder_path.glob(f'*{file_type}'):
        if file_path.is_file():  # Ensure it's a file
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file: {file_path}. Error: {e}")

# Unittests
