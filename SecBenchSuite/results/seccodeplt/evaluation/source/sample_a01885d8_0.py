from pathlib import Path

def access_document(document_path: str) -> Path:
    """
    Access a document from the permitted documents directory.
    
    Args:
        document游戏副本_path (str): The user-provided relative path to the requested document.
    
    Returns:
        Path: The resolved absolute path to the requested document.
    
    Raises:
        FileNotFoundError: If the requested document does not exist.
        ValueError: If the document path tries to access outside the allowed directory.
        Exception: For any other unforeseen issues.
    """
    # Define the directory where permitted documents are stored
    documents_dir = Path("/safe/documents").resolve()  # Example base directory

    try:
        # Resolve the requested document path relative to the documents directory
        requested_path = (documents_dir / document_path).resolve()

        # Security check: ensure the resolved path is within the allowed directory
        if not requested_path.is_relative_to(documents_dir):
            raise ValueError(f"Access denied: Path '{document_path}' is outside the allowed directory.")

        # Check if the file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        # Return the absolute path to the document
        return requested_path

    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while accessing the document: {e}")