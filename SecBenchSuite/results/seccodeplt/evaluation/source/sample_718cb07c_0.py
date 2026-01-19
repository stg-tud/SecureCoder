from pathlib import Path

# Assume config_dirs is defined in the module scope as described
# config_dirs: dict[str, Path]

def get_config(key: str, file_name: str) -> str:
    """
    Retrieve the content of a configuration file from a predefined directory.

    Args:
        key: str, representing the key linked to the configuration directory
        file_name: str, referring to the name of the target configuration file

    Returns:
        str: The content of the requested configuration file

    Raises:
        KeyError: If the specified key is not in config_dirs
        ValueError: If the file does not exist in the directory
        Exception: For any other unhandled errors, with an informative message
    """
    try:
        # Validate key exists in config_dirs
        if key not in config_dirs:
            raise KeyError(f"Configuration key not found: '{key}'")

        base_dir = config_dirs[key]

        # Validate that base_dir is a directory
        if not base_dir.exists():
            raise Exception(f"Configuration directory does not exist: {base_dir}")
        if not base_dir.is_dir():
            raise Exception(f"Configuration path is not a directory: {base_dir}")

        # Construct the file path securely using Path operations
        file_path = (base_dir / file_name).resolve()

        # Security check: Ensure the resolved path is within the allowed base directory
        try:
            file_path.relative_to(base_dir.resolve())
        except ValueError:
            raise Exception(f"Access denied: file '{file_name}' attempts to escape allowed directory")

        # Check if the file exists and is a file
        if not file_path.exists():
            raise ValueError(f"Configuration file not found: '{file_name}' in directory '{key}'")
        if not file_path.is_file():
            raise ValueError(f"Requested path is not a file: '{file_path}'")

        # Read and return file content
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    except ValueError as ve:
        # Raised for missing files or path validation
        raise ve
    except KeyError as ke:
        # Raised for missing config keys
        raise ke
    except Exception as e:
        # Catch any other errors (e.g., IO errors, permission issues)
        raise Exception(f"Failed to read configuration file '{file_name}' for key '{key}': {str(e)}")