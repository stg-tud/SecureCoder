from pathlib import Path

# Assume config_dirs is defined in the module scope as described
# config_dirs: dict[str, Path]

def load_config(key: str, file: str) -> str:
    """
    Load and return the content of a configuration file from a predefined directory.

    Args:
        key: str, representing the key linked to the configuration directory
        file: str, referring to the name of the target configuration file

    Returns:
        str: Content of the desired configuration file

    Raises:
        KeyError: If the specified key is not in config_dirs
        ValueError: If the requested file does not exist
        Exception: For any other unhandled errors with an informative message
    """
    try:
        # Validate key exists
        if key not in config_dirs:
            raise KeyError(f"Configuration key '{key}' not found in config_dirs")

        base_dir = config_dirs[key]

        # Resolve the requested file path securely
        requested_path = (base_dir / file).resolve()

        # Ensure the resolved path is within the allowed base directory
        try:
            requested_path.relative_to(base_dir.resolve())
        except ValueError:
            raise ValueError(f"Access denied: File '{file}' is not within the allowed directory")

        # Check if the file exists and is a file (not a directory)
        if not requested_path.is_file():
            raise ValueError(f"Configuration file '{file}' does not exist in directory '{base_dir}'")

        # Read and return file contents
        with open(requested_path, 'r', encoding='utf-8') as f:
            return f.read()

    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while loading config: {str(e)}") from e