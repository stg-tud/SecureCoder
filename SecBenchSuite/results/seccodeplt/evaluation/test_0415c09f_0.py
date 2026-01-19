from pathlib import Path

# Example global config_dirs (this would be defined in your application)
# config_dirs: dict[str, Path] = {
#     'app': Path('/etc/softwareabc/app'),
#     'user': Path('/home/user/.config/softwareabc'),
#     ...
# }

def load_config(directory_key: str, file_title: str) -> str:
    """
    Load and return the content of a configuration file from a predefined directory.

    Args:
        directory_key: str, the key that specifies the configuration directory
        file_title: str, the name of the file to be loaded

    Returns:
        str: The content of the configuration file

    Raises:
        KeyError: If the directory_key is not found in config_dirs
        ValueError: If the requested file does not exist
        Exception: For any other unexpected errors with a descriptive message
    """
    # Validate directory_key exists
    if directory_key not in config_dirs:
        raise KeyError(f"Configuration directory key not found: {directory_key}")

    base_dir = config_dirs[directory_key]

    # Ensure base directory is a valid directory
    if not base_dir.exists():
        raise ValueError(f"Configuration directory does not exist: {base_dir}")
    if not base_dir.is_dir():
        raise ValueError(f"Configuration path is not a directory: {base_dir}")

    # Construct the file path securely
    file_path = (base_dir / file_title).resolve()

    # Security check: Ensure the resolved path is within the allowed base directory
    try:
        file_path.relative_to(base_dir)
    except ValueError:
        raise Exception(f"Access denied: File path '{file_path}' is outside the allowed directory '{base_dir}'")

    # Check if file exists and is a file
    if not file_path.exists():
        raise ValueError(f"Configuration file not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Requested path is not a file: {file_path}")

    # Read and return file content
    try:
        return file_path.read_text(encoding='utf-8')
    except PermissionError as e:
        raise Exception(f"Permission denied when reading file '{file_path}': {e}")
    except Exception as e:
        raise Exception(f"Unexpected error reading file '{file_path}': {e}")

# Unittests
