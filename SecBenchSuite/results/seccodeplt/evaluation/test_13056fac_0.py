from pathlib import Path

def fetch_file(file_path: str, root_dir: Path) -> Path:
    """
    Fetch a file from a secure directory by resolving its absolute path,
    ensuring the path stays within the allowed root directory.

    Args:
        file_path (str): The relative path to the desired document.
        root_dir (Path): The root directory from which files are allowed to be accessed.

    Returns:
        Path: The absolute path to the requested file.

    Raises:
        FileNotFoundError: If the requested file does not exist.
        ValueError: If the resolved path falls outside the permissible root directory.
        Exception: For any other unexpected errors (e.g., permission issues).
    """
    try:
        # Resolve the requested file path relative to root_dir and ensure it's absolute and normalized
        requested_path = (root_dir / file_path).resolve()

        # Ensure the resolved path is within the root directory
        if not requested_path.is_relative_to(root_dir):
            raise ValueError(f"Access denied: Path '{file_path}' attempts to access outside the allowed directory.")

        # Check if the file actually exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: '{file_path}'")

        return requested_path

    except FileNotFoundError:
        # Re-raise to maintain specific exception type
        raise
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Catch any other unforeseen issues (e.g., permission errors, invalid paths)
        raise Exception(f"An unexpected error occurred while accessing the file: {str(e)}")

# Unittests
