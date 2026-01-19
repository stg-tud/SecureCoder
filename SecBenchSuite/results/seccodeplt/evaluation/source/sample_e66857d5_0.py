from pathlib import Path

# Assume config_dirs is defined in the module scope as per context
# config_dirs: dict[str, Path] = { ... }

def load_config(config_code: str, file_title: str) -> str:
    """
    Load and return the content of a configuration file.

    Args:
        config_code (str): The key identifying the configuration directory.
        file_title (str): The name of the file to retrieve.

    Returns:
        str: The content of the configuration file.

    Raises:
        KeyError: If config_code is not in config_dirs.
        ValueError: If the specified file does not exist.
        Exception: For any other unforeseen errors, with an informative message.
    """
    # Validate that config_code exists
    if config_code not in config_dirs:
        raise KeyError(f"Configuration code '{config_code}' not found in config_dirs.")

    base_dir: Path = config_dirs[config_code]

    # Resolve the requested file path securely
    try:
        # Construct the file path using only the filename (prevents path injection)
        file_path = (base_dir / file_title).resolve()

        # Security check: Ensure the file path is within the authorized base directory
        base_dir_resolved = base_dir.resolve()
        if not file_path.is_relative_to(base_dir_resolved):
            raise ValueError(f"Access denied: File '{file_title}' is outside the allowed directory.")

        # Check if the file exists and is a file
        if not file_path.is_file():
            raise ValueError(f"File '{file_title}' does not exist in directory '{base_dir}'.")

        # Read and return file content
        return file_path.read_text(encoding='utf-8')

    except ValueError as ve:
        # Re-raise ValueError for file not found or path issues
        raise ve
    except Exception as e:
        # Catch any other unforeseen errors (e.g., permission issues, I/O errors)
        raise Exception(f"Unexpected error while loading config '{file_title}' for '{config_code}': {str(e)}") from e