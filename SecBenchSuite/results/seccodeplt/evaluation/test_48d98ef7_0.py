from pathlib import Path

# Example context (to be defined in actual usage)
config_dirs: dict[str, Path] = {
    # 'app1': Path('/etc/softwareabc/app1'),
    # 'app2': Path('/etc/softwareabc/app2'),
    # Add actual config directories as needed
}

def retrieve_config(key: str, file_name: str) -> str:
    """
    Retrieve and return the contents of a configuration file from a predefined directory.

    - key: str, the key that specifies the configuration directory
    - file_name: str, the name of the file to be loaded

    Returns:
        str: The content of the configuration file.

    Raises:
        KeyError: If the provided key is not found in config_dirs.
        ValueError: If the requested file does not exist at the expected location.
        Exception: For any other unexpected errors, with a descriptive message.
    """
    try:
        # Validate key exists in config_dirs
        if key not in config_dirs:
            raise KeyError(f"Configuration key not found: {key}")

        base_dir = config_dirs[key]

        # Construct the file path securely
        requested_path = (base_dir / file_name).resolve()

        # Security check: Ensure the resolved path is within the allowed base directory
        try:
            requested_path.relative_to(base_dir.resolve())
        except ValueError:
            raise ValueError(f"Access denied: File '{file_name}' attempts to access outside allowed directory for key '{key}'")

        # Check if the file exists and is a file
        if not requested_path.is_file():
            raise ValueError(f"Configuration file not found: {requested_path}")

        # Read and return file content
        with open(requested_path, 'r', encoding='utf-8') as f:
            return f.read()

    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Unexpected error while retrieving config: {e}") from e

# Unittests
