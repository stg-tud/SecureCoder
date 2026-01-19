import os

def clear_temp_data(temp_data_path: str) -> bool:
    """
    Removes the temporary file at the given path.

    This function attempts to delete the file directly without first checking
    for its existence, to avoid a TOCTOU race condition in a multi-user environment.

    Args:
        temp_data_path (str): Path to the temporary file to be removed.

    Returns:
        bool: True if the file was successfully deleted or was already absent.
              False if the file exists but could not be removed (e.g., permission denied).
    """
    try:
        os.remove(temp_data_path)
        return True
    except FileNotFoundError:
        # File doesn't exist, which is acceptable
        return True
    except PermissionError:
        # File exists but cannot be deleted (e.g., insufficient permissions)
        return False
    except IsADirectoryError:
        # The path is a directory, not a file
        return False
    except OSError:
        # Any other OS-level error (e.g., I/O error, resource busy)
        return False
    except Exception:
        # Catch-all for any other unforeseen exceptions (e.g., type errors in path)
        return False

# Unittests
