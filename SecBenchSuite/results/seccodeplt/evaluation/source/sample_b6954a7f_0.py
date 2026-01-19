from pathlib import Path

def find_document(file_path: str, allowed_dir: Path) -> Path:
    """
    Resolve the absolute path of a requested document, ensuring it resides within the allowed directory.

    Args:
        file_path: str, the user-provided relative path to a requested document
        allowed_dir: Path, representing the directory that holds the permitted documents

    Returns:
        Path: the resolved absolute path to the requested document

    Raises:
        FileNotFoundError: if the requested document does not exist
        ValueError: if the resolved path is outside the allowed directory
        Exception: for any other unforeseen issues
    """
    try:
        # Resolve the requested file path relative to the allowed directory
        requested_path = (allowed_dir / file_path).resolve()

        # Resolve the allowed directory to ensure consistency
        allowed_dir_resolved = allowed_dir.resolve()

        # Check if the requested path is within the allowed directory
        # This prevents directory traversal attacks (e.g., using '../')
        try:
            requested_path.relative_to(allowed_dir_resolved)
        except ValueError:
            raise ValueError(f"Access denied: '{file_path}' is outside the allowed directory")

        # Verify that the file actually exists
        if not requested_path.is_file():
            raise FileNotFoundError(f"Document not found: {file_path}")

        return requested_path

    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while accessing the document: {str(e)}")