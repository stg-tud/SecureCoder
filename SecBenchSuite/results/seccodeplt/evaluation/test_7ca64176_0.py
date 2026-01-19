import os

def remove_temp_file(temp_path: str) -> bool:
    """
    Safely removes a temporary file if it exists.
    
    This function avoids TOCTOU race conditions by attempting deletion directly
    without first checking for file existence. This ensures atomicity between 
    the check and deletion steps.

    Args:
        temp_path: str, the file system path to the temporary file to be deleted.

    Returns:
        bool: True if the file was successfully deleted or did not exist.
              False if the deletion failed due to permissions or other I/O errors.
              
    Security Note:
        Directly attempting os.remove() without prior existence check prevents
        TOCTOU race conditions where the file could be replaced between check and delete.
    """
    try:
        os.remove(temp_path)
        return True
    except FileNotFoundError:
        # File doesn't exist - this is acceptable; return True
        return True
    except (PermissionError, OSError):
        # Failed to delete due to permissions or other OS-level issues
        return False

# Unittests
