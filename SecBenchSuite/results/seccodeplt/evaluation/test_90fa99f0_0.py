import os

def delete_temporary_file(file_path_temp: str) -> bool:
    """
    Safely deletes a temporary file if it exists.
    
    This function avoids TOCTOU (Time-of-Check-To-Time-Use) race conditions by
    attempting to delete the file directly without first checking if it exists.
    The existence check and deletion are combined into a single atomic operation
    via os.remove(), which is safer in multi-user environments.
    
    Args:
        file_path_temp: The file system path to the temporary file to be deleted.
    
    Returns:
        bool: True if the file was successfully deleted or did not exist.
              False if the deletion failed due to an error (e.g. permission denied).
    """
    try:
        os.remove(file_path_temp)
        return True
    except FileNotFoundError:
        # File does not exist, which is acceptable
        return True
    except (PermissionError, IsADirectoryError, OSError):
        # Permission denied, path is a directory, or other OS-level error
        return False

# Unittests
