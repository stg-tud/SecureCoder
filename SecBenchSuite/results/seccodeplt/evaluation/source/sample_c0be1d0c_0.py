from pathlib import Path

# Assume 'directories' is a module-level dictionary mapping keys to Path objects
directories = {}  # This should be populated with actual directory mappings

def fetch_log_file(directory_key: str, relative_path: str) -> Path:
    """
    Retrieves the absolute path of a log file based on a directory key and a relative file path.
    
    Security: Ensures the resolved path stays within the allowed directory to prevent path traversal attacks.
    
    Args:
        directory_key: A string that specifies the directory key to look up.
        relative_path: A string, the relative path of the file within the selected directory.
    
    Returns:
        The full absolute path (Path) of the requested log file.
    
    Raises:
        KeyError: If the specified directory_key does not exist in the directories.
        FileNotFoundError: If the log file cannot be found with the relative path inside the directory.
        Exception: For any other errors, with a suitable message.
    """
    try:
        # Step 1: Validate directory_key exists
        if directory_key not in directories:
            raise KeyError(f"Directory key '{directory_key}' does not exist.")
        
        base_dir = directories[directory_key]
        
        # Ensure base_dir is a directory
        if not base_dir.is_dir():
            raise Exception(f"Base path for key '{directory_key}' is not a directory: {base_dir}")
        
        # Step 2: Resolve the requested file path
        requested_path = (base_dir / relative_path).resolve()
        
        # Step 3: Security check - ensure the resolved path is within the base directory
        try:
            requested_path.relative_to(base_dir)
        except ValueError:
            raise Exception(f"Access denied: attempted path traversal detected for '{relative_path}'.")
        
        # Step 4: Verify that the file exists
        if not requested_path.is_file():
            raise FileNotFoundError(f"Log file not found: {requested_path}")
        
        return requested_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Re-raise known exceptions or wrap unexpected ones
        raise Exception(f"Error fetching log file: {str(e)}") from e