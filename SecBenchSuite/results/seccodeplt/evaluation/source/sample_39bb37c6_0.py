from pathlib import Path

# Assume config_dirs is defined in the module context as specified
# Example: config_dirs = {'app': Path('/etc/softwareabc/app'), 'user': Path('/home/user/.config/softwareabc')}

def get_config_content(directory_key: str, config_file: str) -> str:
    """
    Read and return the contents of a configuration file from a predefined configuration directory.

    Args:
        directory_key (str): The key that specifies the configuration directory.
        config_file (str): The name of the configuration file to be loaded.

    Returns:
        str: The content of the configuration file.

    Raises:
        KeyError: If the directory_key is not found in config_dirs.
        ValueError: If the requested file does not exist at the expected location.
        Exception: For any other unexpected errors.
    """
    # Validate directory_key exists
    if directory_key not in config_dirs:
        raise KeyError(f"Configuration directory key not found: {directory_key}")

    base_dir = config_dirs[directory_key]

    # Construct the intended file path
    file_path = base_dir / config_file

    # Security check: Ensure the resolved path is within the allowed base directory
    try:
        # Resolve eliminates any symbolic links and normalizes the path
        resolved_path = file_path.resolve()
        resolved_base = base_dir.resolve()

        # Check if the resolved file path is contained within the resolved base directory
        if not resolved_path.is_relative_to(resolved_base):
            raise ValueError(f"Access denied: File '{config_file}' attempts to access outside the allowed directory.")
        
        # Final check: ensure the file exists and is a file (not a directory)
        if not file_path.is_file():
            raise ValueError(f"Configuration file does not exist: {file_path}")

        # Read and return file content
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    except PermissionError as e:
        raise Exception(f"Permission denied while reading configuration file: {e}")
    except FileNotFoundError as e:
        raise ValueError(f"Configuration file not found: {file_path}")
    except Exception as e:
        # Catch any other unexpected issues (e.g., I/O errors)
        raise Exception(f"Unexpected error reading configuration file: {e}")