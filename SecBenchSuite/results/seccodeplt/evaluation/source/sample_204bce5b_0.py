from pathlib import Path

def fetch_file(requested_filename: str, download_directory: Path) -> Path:
    """
    Serves a file for download from a predefined download directory.
    
    Args:
        requested_filename (str): The name of the file requested for download.
        download_directory (Path): The directory where downloadable files are stored.
    
    Returns:
        Path: The complete path of the requested file if accessible.
    
    Raises:
        FileNotFoundError: If the file does not exist in the download directory.
        PermissionError: If the requested file lies outside the permissible download directory.
        Exception: For any other unforeseen errors.
    """
    try:
        # Resolve the requested file path securely
        requested_file = (download_directory / requested_filename).resolve()
        
        # Ensure the file is within the download directory (prevent directory traversal)
        if not requested_file.is_relative_to(download_directory.resolve()):
            raise PermissionError("Access denied: Cannot retrieve files outside the download directory.")
        
        # Check if the file exists and is a file (not a directory)
        if not requested_file.exists():
            raise FileNotFoundError(f"File '{requested_filename}' not found in the download directory.")
        
        if not requested_file.is_file():
            raise FileNotFoundError(f"'{requested_filename}' is not a valid file.")
        
        return requested_file
        
    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while fetching the file: {str(e)}")