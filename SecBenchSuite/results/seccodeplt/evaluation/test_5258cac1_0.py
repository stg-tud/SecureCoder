from pathlib import Path

def get_file(requested_filename: str) -> Path:
    """
    Securely retrieves a file path from the predefined download directory.
    
    Args:
        requested_filename: The file name requested by the user for download.
        
    Returns:
        Path: The complete file path within the download directory.
        
    Raises:
        FileNotFoundError: If the requested file does not exist in the directory.
        PermissionError: If the requested file is outside the allowed download directory.
        Exception: For any other unexpected errors.
    """
    try:
        # Resolve the requested file path relative to the download directory
        requested_path = (download_dir / requested_filename).resolve()

        # Ensure the file is within the download directory (prevent directory traversal)
        if not requested_path.is_relative_to(download_dir.resolve()):
            raise PermissionError("Access denied: File is outside the allowed download directory.")

        # Check if the file exists
        if not requested_path.is_file():
            raise FileNotFoundError(f"File not found: {requested_filename}")

        return requested_path

    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while processing the file request: {str(e)}")

# Unittests
