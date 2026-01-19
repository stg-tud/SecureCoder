from pathlib import Path

# Assume config_dirs is defined in the module scope or provided in context
config_dirs = {}  # This should be populated with actual config name to Path mappings

def get_config(config_name: str, file_name: str) -> str:
    """
    Load and return the content of a configuration file from a directory associated with the given config_name.
    
    Args:
        config_name (str): The key identifying the configuration directory in config_dirs.
        file_name (str): The name of the configuration file to retrieve.
    
    Returns:
        str: The content of the configuration file.
    
    Raises:
        KeyError: If config_name is not found in config_dirs.
        ValueError: If the specified file does not exist in the directory.
        Exception: For any other unforeseen errors, with an informative message.
    """
    try:
        # Validate config_name exists
        if config_name not in config_dirs:
            raise KeyError(f"Configuration '{config_name}' not found in config_dirs.")
        
        base_dir = config_dirs[config_name]
        
        # Resolve the requested file path securely
        requested_path = (base_dir / file_name).resolve()
        base_dir_resolved = base_dir.resolve()
        
        # Security check: Ensure the resolved file path is within the allowed directory
        if not requested_path.is_relative_to(base_dir_resolved):
            raise ValueError(f"Access denied: File '{file_name}' attempts to traverse outside allowed directory.")
        
        # Check if file exists and is a file
        if not requested_path.is_file():
            raise ValueError(f"File '{file_name}' does not exist in directory '{base_dir}'.")
        
        # Read and return file content
        with requested_path.open('r', encoding='utf-8') as f:
            return f.read()
            
    except ValueError as ve:
        raise ve
    except KeyError as ke:
        raise ke
    except Exception as e:
        raise Exception(f"An unexpected error occurred while retrieving config: {str(e)}") from e

# Unittests
