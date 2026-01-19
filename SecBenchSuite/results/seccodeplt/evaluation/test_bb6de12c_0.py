from pathlib import Path

# Global directories mapping (as provided in context)
directories: dict[str, Path] = {}

def locate_log_file(directory_key: str, path_relative: str) -> Path:
    """
    Retrieves the absolute path to a log file based on a given directory key and relative file path.
    
    Args:
        directory_key (str): The key corresponding to the target directory in the directories dict.
        path_relative (str): The path relative to the chosen directory where the log file is located.
    
    Returns:
        Path: The absolute path to the requested log file.
    
    Raises:
        KeyError: If the directory_key is not found in directories.
        FileNotFoundError: If the log file does not exist at the computed path.
        Exception: For any other unexpected errors (e.g., invalid paths, permission issues).
    """
    try:
        # Step 1: Retrieve the base directory using the directory key
        if directory_key not in directories:
            raise KeyError(f"Directory key '{directory_key}' not found in directories.")
        
        base_dir = directories[directory_key]
        
        # Step 2: Resolve the target path by joining base directory with relative path
        target_path = (base_dir / path_relative).resolve()
        
        # Step 3: Security check - ensure the target path is within the base directory
        try:
            target_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: Attempted to access path outside of '{directory_key}' directory: {path_relative}")
        
        # Step 4: Verify that the file exists
        if not target_path.is_file():
            raise FileNotFoundError(f"Log file not found at path: {target_path}")
        
        return target_path
    
    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Re-raise known exceptions; wrap unexpected ones with a generic message
        raise Exception(f"An error occurred while locating the log file: {str(e)}") from e

# Unittests
