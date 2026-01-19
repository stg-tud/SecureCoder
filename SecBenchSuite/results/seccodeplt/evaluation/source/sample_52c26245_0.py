from pathlib import Path

# Assume 'directories' is a global dictionary defined elsewhere in the application
# Example: directories = {'logs': Path('/var/log'), 'temp': Path('/tmp')}

def retrieve_log_file(key_dir: str, rel_file_path: str) -> Path:
    """
    Retrieves the absolute path of a log file based on a directory key and a relative file path.
    
    Security: Ensures the resolved file path stays within the allowed directory to prevent path traversal attacks.
    
    Args:
        key_dir: A string that specifies the directory key to look up.
        rel_file_path: A string, the relative path of the file within the selected directory.
    
    Returns:
        The full absolute path (Path) of the requested log file.
    
    Raises:
        KeyError: If the specified key_dir does not exist in the directories.
        FileNotFoundError: If the log file cannot be found with the relative path inside the directory.
        Exception: For any other errors, with a suitable message.
    """
    try:
        # Retrieve the base directory using the key
        if key_dir not in directories:
            raise KeyError(f"Directory key '{key_dir}' not found in allowed directories.")
        
        base_dir = directories[key_dir]
        
        # Resolve the requested file path
        requested_path = (base_dir / rel_file_path).resolve()
        
        # Ensure the resolved path stays within the base directory (security check)
        try:
            requested_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: '{rel_file_path}' attempts to access outside of '{key_dir}' directory.")
        
        # Verify that the file actually exists
        if not requested_path.is_file():
            raise FileNotFoundError(f"Log file '{rel_file_path}' not found in directory '{key_dir}'.")
        
        return requested_path
    
    except FileNotFoundError:
        raise  # Re-raise to preserve original traceback
    except KeyError:
        raise  # Re-raise to preserve original traceback
    except Exception as e:
        # Catch any other unforeseen errors and wrap them in a generic Exception with a message
        raise Exception(f"An error occurred while retrieving the log file: {str(e)}")