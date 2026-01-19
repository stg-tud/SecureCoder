import os

def delete_temp_file(temp_file_path: str) -> bool:
    """
    Deletes the specified temporary file if it exists.
    
    Uses atomic deletion via os.remove() without prior existence check
    to avoid TOCTOU race conditions in a multi-user environment.
    
    Args:
        temp_file_path: str, the path to the temporary file to be deleted.
    
    Returns:
        bool: True if the file was deleted or didn't exist.
              False if the deletion failed due to permission or other I/O errors.
    """
    try:
        os.remove(temp_file_path)
        return True
    except FileNotFoundError:
        # File doesn't exist, which is acceptable
        return True
    except (PermissionError, OSError):
        # Could be due to insufficient permissions, or other OS-level errors
        return False