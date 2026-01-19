from pathlib import Path

def get_document(document_path: str) -> Path:
    """
    Fetch a document from the secure document root directory.
    
    Args:
        document_path: str, the relative path to the desired document, as given by the user
    
    Returns:
        Path: The absolute file path of the document if it exists and is within the allowed directory
    
    Raises:
        FileNotFoundError: If the requested file does not exist
        ValueError: If the document path attempts to access locations outside the document_root
        Exception: For any other unexpected errors
    """
    # Define the root directory from which files can be accessed
    document_root = Path("/safe/document/root").resolve()  # Example secure root directory

    try:
        # Construct the requested path relative to the document root
        requested_path = (document_root / document_path).resolve()

        # Security check: Ensure the resolved path is within the document_root
        if not requested_path.is_relative_to(document_root):
            raise ValueError(f"Access denied: '{document_path}' is outside the allowed directory")

        # Check if the file exists and is a file (not a directory)
        if not requested_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        if not requested_path.is_file():
            raise FileNotFoundError(f"Document is not a file: {document_path}")

        return requested_path

    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Unexpected error while retrieving document: {str(e)}")

# Unittests
