from pathlib import Path

def find_log_file(key_dir: str, path_rel: str) -> Path:
    """
    Fetches the absolute file path of a log based on a directory key and relative file path.
    
    Validates that the resulting file path lies within the specified directory to prevent
    path traversal attacks or unauthorized file access.
    
    Args:
        - key_dir: A string that serves as the identifier for the directory.
        - path_rel: A string representing the relative file path inside the directory.
    
    Returns:
        The absolute path of the log file as a Path object.
    
    Raises:
        KeyError: If the specified directory key does not exist in the dictionary.
        FileNotFoundError: If the log file cannot be found at the provided path.
        Exception: If any unexpected error occurs, with an appropriate message.
    
    Context:
        directories: A dictionary mapping directory keys (type str) to their respective Path objects,
                     representing full directory paths.
    """
    # External context (assumed to be available in the scope)
    global directories
    
    try:
        # Check if the directory key exists
        if key_dir not in directories:
            raise KeyError(f"Directory key '{key_dir}' not found.")
        
        base_dir = directories[key_dir]
        
        # Resolve the requested file path
        file_path = (base_dir / path_rel).resolve()
        
        # Security check: ensure the file_path is within the base_dir
        try:
            file_path.relative_to(base_dir)
        except ValueError:
            raise Exception(f"Access denied: attempted to access file outside of directory '{key_dir}'.")
        
        # Check if the file actually exists
        if not file_path.is_file():
            raise FileNotFoundError(f"Log file not found: '{file_path}'")
        
        return file_path
        
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")