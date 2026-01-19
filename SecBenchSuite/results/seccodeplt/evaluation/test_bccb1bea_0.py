import os
from threading import Lock

# Global lock for thread-safe file operations
_file_access_lock = Lock()

def read_file_if_exists(filepath: str) -> str:
    """
    Reads the content of a file if it exists at the specified path.
    
    Args:
        filepath: str, the path to the file to be read.
    
    Return:
        str, the content of the file at the specified path. If the file does not exist, return None.
    
    Security:
        Uses a thread lock to ensure atomicity between file existence check and read operation,
        preventing race conditions in a multithreaded environment.
    """
    with _file_access_lock:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    return file.read()
            except (IOError, OSError):
                # If there's any issue reading the file (e.g. permission, corruption), treat as non-existent
                return None
        return None

# Unittests
