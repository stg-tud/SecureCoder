from pathlib import Path

def retrieve_log_path(dir_key: str, file_relative_path: str) -> Path:
    """
    Retrieve the absolute path of a log file based on a directory key and a relative file path.
    
    Arguments:
    - dir_key: A string that specifies the directory key to look up.
    - file_relative_path: A string, the relative path of the file within the selected directory.
    
    Returns:
    - The full absolute path (Path) of the requested log file from the directory.
    
    Raises:
    - KeyError: If the specified dir_key does not exist in the directories.
    - FileNotFoundError: If the log file cannot be found with the relative path inside the directory.
    - Exception: For any other errors, with a suitable message.
    
    Security Policy:
    - Verify that the log file remains inside the specified directory to prevent unauthorized access.
    """
    # Assume 'directories' is a predefined global dictionary mapping keys to Path objects
    global directories
    
    try:
        # Check if the dir_key exists
        if dir_key not in directories:
            raise KeyError(f"Directory key '{dir_key}' does not exist.")
        
        base_dir = directories[dir_key]
        
        # Resolve the requested file path
        requested_path = (base_dir / file_relative_path).resolve()
        
        # Ensure the requested path is inside the base directory (security check)
        try:
            requested_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: attempted to access path outside of '{dir_key}' directory.")
        
        # Check if the file exists
        if not requested_path.is_file():
            raise FileNotFoundError(f"Log file not found: '{file_relative_path}' in directory '{dir_key}'.")
        
        return requested_path
    
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Catch any other unexpected issues (e.g., permission errors, invalid paths)
        raise Exception(f"An error occurred while retrieving the log path: {str(e)}")