def remove_temporary_file(path_to_temp_file: str) -> bool:
    """
    Safely removes a temporary file if it exists, avoiding TOCTOU race conditions.
    
    Instead of checking for file existence first (which could create a race condition),
    we directly attempt to remove the file and handle any resulting errors.
    
    Args:
        path_to_temp_file: The file system path to the temporary file to be deleted.
    
    Returns:
        True if the file was successfully deleted or did not exist.
        False if an error occurred during deletion (e.g., permission denied).
    """
    try:
        os.remove(path_to_temp_file)
        return True
    except FileNotFoundError:
        # File does not exist, which is acceptable
        return True
    except (PermissionError, IsADirectoryError, OSError):
        # Permission denied, path is a directory, or other OS-level error
        return False

# Unittests
