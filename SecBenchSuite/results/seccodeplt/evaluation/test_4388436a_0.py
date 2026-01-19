from pathlib import Path

# Assume config_dirs is defined in the module scope or injected
config_dirs: dict[str, Path] = {}

def retrieve_config(config_id: str, target_file: str) -> str:
    """
    Retrieve the content of a configuration file from a predefined configuration directory.

    Args:
        config_id (str): Key identifying the configuration directory in config_dirs.
        target_file (str): Name of the configuration file to retrieve.

    Returns:
        str: Content of the target configuration file.

    Raises:
        KeyError: If the config_id is not found in config_dirs.
        ValueError: If the target_file does not exist in the specified directory.
        Exception: For any other unhandled file system or I/O errors.
    """
    try:
        # Validate config_id exists
        if config_id not in config_dirs:
            raise KeyError(f"Configuration ID '{config_id}' not found.")

        config_dir = config_dirs[config_id]

        # Ensure target_file is a valid relative filename (prevent path traversal)
        try:
            # Use Path to sanitize and resolve the filename safely
            file_path = (config_dir / target_file).resolve()
            # Check that the final path is within the allowed config directory
            config_dir_resolved = config_dir.resolve()
            if not file_path.is_relative_to(config_dir_resolved):
                raise ValueError(f"Access denied: '{target_file}' attempts to traverse outside allowed directory.")
        except Exception as e:
            # Handle cases like is_relative_to not available (Python < 3.9) or invalid paths
            # Fallback: ensure no '/../' or absolute paths are allowed
            if '..' in target_file.split('/') or Path(target_file).is_absolute():
                raise ValueError(f"Invalid filename: '{target_file}' contains path traversal attempts.")
            file_path = config_dir / target_file
            if not file_path.resolve().is_relative_to(config_dir_resolved):
                raise ValueError(f"Access denied: '{target_file}' resolves outside allowed directory.")

        # Check if the file exists and is a file
        if not file_path.is_file():
            raise ValueError(f"Configuration file '{target_file}' not found in directory '{config_dir}'.")

        # Read and return file content
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while retrieving configuration: {str(e)}")

# Unittests
