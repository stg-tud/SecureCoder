from pathlib import Path

def fetch_file(request_file: str, download_dir: Path) -> Path:
    """
    Fetch a file from the allowed download directory, ensuring secure access.
    
    Args:
        request_file: str, the file requested by the user for download
        download_dir: Path, the directory from which files can be safely downloaded
    
    Returns:
        Path: the complete file path to the requested file
    
    Raises:
        FileNotFoundError: if the requested file is not found in the directory
        PermissionError: if accessing the requested file is restricted due to it being outside the download directory
        Exception: for any other error conditions
    """
    try:
        # Resolve the requested file path relative to the download directory
        requested_path = (download_dir / request_file).resolve()

        # Ensure the resolved path is within the download directory
        # This prevents directory traversal attacks (e.g., using '../' to escape)
        if not requested_path.is_relative_to(download_dir):
            raise PermissionError("Access to files outside the download directory is not allowed.")

        # Check if the file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File '{request_file}' not found in the download directory.")

        # Ensure the path is not a directory (we want to serve files only)
        if requested_path.is_dir():
            raise FileNotFoundError(f"'{request_file}' is a directory, not a file.")

        return requested_path

    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        # Catch any other unforeseen errors
        raise Exception(f"An error occurred while fetching the file: {str(e)}")

# Unittests
