from pathlib import Path

# Assuming config_dirs is defined in the module/global scope
config_dirs: dict[str, Path] = {}  # This should be initialized with actual paths

def fetch_config(config_key: str, filename: str) -> str:
    """
    Retrieve the content of a configuration file from a predefined directory.

    Args:
        config同行_key: str, the configuration directory key
        filename: str, the name of the file to retrieve

    Returns:
        str: The content of the configuration file

    Raises:
        KeyError: If the config_key is not in config_dirs
        ValueError: If the file does not exist
        Exception: For any other exceptions, with a descriptive message
    """
    try:
        # Validate config_key exists
        if config_key not in config_dirs:
            raise KeyError(f"Configuration key '{config_key}' not found in config_dirs")

        base_dir = config_dirs[config_key]

        # Ensure the filename is a valid relative path (prevent directory traversal)
        file_path = (base_dir / filename).resolve()

        # Security check: Ensure the final path is within the allowed base directory
        if not file_path.is_file():
            raise ValueError(f"Configuration file '{filename}' does not exist in directory for key '{config_key}'")

        if not file_path.parent.resolve().is_relative_to(base_dir.resolve()):
            raise ValueError(f"Invalid file path: '{filename}' attempts to access unauthorized location")

        # Read and return file content
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    except ValueError as ve:
        raise ve
    except KeyError as ke:
        raise ke
    except Exception as e:
        raise Exception(f"An error occurred while fetching config: {str(e)}") from e