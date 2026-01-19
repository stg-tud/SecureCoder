from pathlib import Path

def get_file(filepath: str) -> Path:
    """
    Retrieve the absolute path of a requested file, ensuring it resides within the allowed directory scope.

    Args:
        filepath (str): The relative file path as provided by the user for the requested document.

    Returns:
        Path: The full absolute path to the requested document.

    Raises:
        FileNotFoundError: If the requested file does not exist.
        ValueError: If the file path attempts to access locations outside the allowed directory.
        Exception: For any other issues encountered during processing.
    """
    # Pre-defined directory where documents are stored
    documents_dir = Path("documents").resolve()

    # Resolve the user-provided path within the documents directory
    requested_path = (documents_dir / filepath).resolve()

    try:
        # Ensure the requested path is within the documents directory (security check)
        requested_path.relative_to(documents_dir)
    except ValueError:
        raise ValueError(f"Access denied: Path '{filepath}' attempts to access outside the allowed directory.")

    # Check if the file exists
    if not requested_path.is_file():
        raise FileNotFoundError(f"The requested file '{filepath}' does not exist.")

    return requested_path

# Unittests
