from pathlib import Path

def locate_document(allowed_directory: Path, requested_path: str) -> Path:
    """
    Locate a document within the allowed directory.

    Args:
        allowed_directory (Path): The directory that holds the permitted documents.
        requested_path (str): The user-provided relative path to a requested document.

    Returns:
        Path: The resolved absolute path to the requested document.

    Raises:
        FileNotFoundError: If the requested document does not exist.
        ValueError: If the resolved path is outside the allowed directory.
        Exception: For any other unforeseen issues.
    """
    try:
        # Resolve the requested path within the allowed directory
        # First, create a path from the requested string
        requested_file = Path(requested_path)

        # Prevent absolute paths or paths with '..' that could escape the directory
        # Construct the full path by joining allowed_directory with requested_path
        # Use Path.resolve() to normalize and eliminate any '..' or symbolic links
        resolved_path = (allowed_directory / requested_file).resolve()

        # Ensure the resolved path is still within the allowed directory
        # This prevents directory traversal attacks
        if not resolved_path.is_relative_to(allowed_directory):
            raise ValueError("Requested path is outside the allowed directory.")

        # Check if the file actually exists
        if not resolved_path.exists():
            raise FileNotFoundError(f"Document not found: {requested_path}")

        return resolved_path

    except ValueError as ve:
        # Re-raise ValueError (e.g., path outside allowed directory)
        raise ve
    except FileNotFoundError as fnfe:
        # Re-raise FileNotFoundError
        raise fnfe
    except Exception as e:
        # Catch any other unexpected errors
        raise Exception(f"An unexpected error occurred while locating the document: {str(e)}")