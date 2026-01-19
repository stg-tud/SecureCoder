from pathlib import Path

def retrieve_document(doc_path: str, base_dir: Path) -> Path:
    """
    Retrieves a document based on the provided relative path within the allowed base directory.

    Args:
        doc_path (str): The relative path of the document requested by the user.
        base_dir (Path): The directory from which documents can be retrieved.

    Returns:
        Path: The absolute path of the document.

    Raises:
        FileNotFoundError: If the document does not exist.
        ValueError: If the document path is outside the allowed directory.
        Exception: For any other issues with appropriate messages.
    """
    try:
        # Resolve the requested document path securely
        requested_path = (base_dir / doc_path).resolve()

        # Ensure the base directory is absolute to prevent surprises
        base_dir_resolved = base_dir.resolve()

        # Check if the resolved path is within the allowed base directory
        if not requested_path.is_relative_to(base_dir_resolved):
            raise ValueError(f"Access denied: '{doc_path}' is outside the allowed directory.")

        # Check if the file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"Document not found: '{doc_path}'")

        # Ensure the path points to a file (not a directory)
        if requested_path.is_dir():
            raise FileNotFoundError(f"Document path refers to a directory: '{doc_path}'")

        return requested_path

    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while retrieving the document: {str(e)}")