from pathlib import Path

def download_file(file_name: str) -> Path:
    """
    Serves a file from the predefined download directory.
    
    Args:
        file_name: str, the name of the file that the user wants to download
        
    Returns:
        Path: the full path of the file
        
    Raises:
        FileNotFoundError: if the file does not exist
        PermissionError: if the file is outside the download directory
        Exception: for any other exceptions with proper messages
    """
    # Assume download_dir is defined in the context
    global download_dir
    download_dir: Path
    
    try:
        # Resolve the requested file path
        requested_path = (download_dir / file_name).resolve()
        
        # Resolve the download directory path
        download_dir_resolved = download_dir.resolve()
        
        # Ensure the requested file is within the download directory
        if not requested_path.is_relative_to(download_dir_resolved):
            raise PermissionError(f"Access denied: file '{file_name}' is outside the allowed download directory.")
        
        # Check if the file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: '{file_name}'")
        
        # Return the full path of the file
        return requested_path
        
    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while processing the file request: {str(e)}")