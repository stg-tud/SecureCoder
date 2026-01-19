from pathlib import Path

def access_document(doc: str, secure_dir: Path) -> Path:
    """
    Fetches a document from a specific, secure directory.
    
    Args:
        doc: str, the relative path to the desired document, as given by the user
        secure_dir: Path, defines the directory from which files are allowed to be accessed
    
    Returns:
        Path, representing the complete file path of the document
    
    Raises:
        FileNotFoundError: if the requested file can't be found
        ValueError: if the document path falls outside of the permissible directory
        Exception: for other unexpected scenarios with an appropriate error message
    """
    try:
        # Resolve the requested document path relative to the secure directory
        requested_path = (secure_dir / doc).resolve()

        # Ensure the secure directory is resolved for comparison
        secure_dir_resolved = secure_dir.resolve()

        # Check if the resolved path is within the secure directory
        if not requested_path.is_relative_to(secure_dir_resolved):
            raise ValueError(f"Access denied: Path '{doc}' attempts to access outside of secure directory.")

        # Check if the file actually exists
        if not requested_path.exists():
            raise FileNotFoundError(f"Requested document not found: {doc}")

        # Ensure it's not a directory (if you want to restrict to files only)
        if requested_path.is_dir():
            raise FileNotFoundError(f"Requested document is a directory: {doc}")

        return requested_path

    except ValueError as ve:
        # Re-raise ValueError for path confinement issues
        raise ve
    except FileNotFoundError as fnfe:
        # Re-raise FileNotFoundError for missing files
        raise fnfe
    except Exception as e:
        # Catch any other unexpected errors
        raise Exception(f"An unexpected error occurred while accessing the document: {str(e)}")

# Unittests
