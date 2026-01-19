from pathlib import Path

def fetch_file(file_path: str) -> Path:
    """
    Securely fetches a file from the allowed directory by resolving the user-provided
    relative path and ensuring it stays within the root directory.

    Args:
        file_path: str, the relative file path as provided by the user for the requested document

    Returns:
        Path: the full absolute path to the requested document

    Raises:
        FileNotFoundError: if the requested file does not exist
        ValueError: if the file path attempts to access outside the allowed directory scope
        Exception: for any other issues (e.g., invalid path, I/O errors)
    """
    # Pre-defined root directory where documents are stored
    root_dir = Path("documents").resolve()  # Example root directory; can be configured

    try:
        # Resolve the user input to an absolute path, but relative to root_dir
        requested_path = (root_dir / file_path).resolve()

        # Security check: Ensure the requested path is within the root directory
        if not requested_path.is_relative_to(root_dir):
            raise ValueError(f"Access denied: Path '{file_path}' attempts to access outside allowed directory.")

        # Check if the file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"The requested file '{file_path}' was not found.")

        # Optional: Ensure it's a file (not a directory), if strictly retrieving files
        if not requested_path.is_file():
            raise Exception(f"The path '{file_path}' is not a file.")

        return requested_path

    except ValueError as ve:
        # Re-raise ValueError for path traversal attempts
        raise ve
    except FileNotFoundError as fnfe:
        # Re-raise FileNotFoundError for missing files
        raise fnfe
    except Exception as e:
        # Catch-all for other unforeseen issues
        raise Exception(f"An error occurred while accessing the file: {str(e)}")