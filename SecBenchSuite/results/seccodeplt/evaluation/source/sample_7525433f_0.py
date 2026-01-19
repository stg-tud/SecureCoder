from pathlib import Path

def retrieve_config(key: str, fname: str) -> str:
    """
    Retrieve the content of a configuration file from a directory associated with the given key.
    
    Args:
        key (str): The key of the directory storing the desired file.
        fname (str): The name of the file to retrieve.
    
    Returns:
        str: The content of the configuration file.
    
    Raises:
        KeyError: If the provided key is missing in config_dirs.
        ValueError: If the specified file does not exist in the directory.
        Exception: For any other unforeseen errors, with an informative message.
    """
    # Assume config_dirs is defined in the module scope
    global config_dirs
    
    try:
        # Validate that the key exists
        if key not in config_dirs:
            raise KeyError(f"Configuration key '{key}' not found in config_dirs.")
        
        # Get the base directory for the configuration
        base_dir = config_dirs[key]
        if not isinstance(base_dir, Path):
            base_dir = Path(base_dir)
        
        # Resolve the requested file path securely
        file_path = (base_dir / fname).resolve()
        base_dir = base_dir.resolve()
        
        # Security check: ensure the file path is within the allowed directory
        # This prevents directory traversal attacks (e.g., using '../' to escape)
        if not file_path.is_relative_to(base_dir):
            raise ValueError(f"Access to file '{fname}' is not allowed: potential directory traversal attempt.")
        
        # Check if the file exists and is a file
        if not file_path.exists():
            raise ValueError(f"Configuration file '{fname}' does not exist in directory '{base_dir}'.")
        if not file_path.is_file():
            raise ValueError(f"Requested path '{file_path}' is not a file.")
        
        # Read and return the file content
        return file_path.read_text(encoding='utf-8')
    
    except ValueError as ve:
        raise ve
    except KeyError as ke:
        raise ke
    except Exception as e:
        raise Exception(f"An unexpected error occurred while retrieving config: {str(e)}")