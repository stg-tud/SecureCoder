from pathlib import Path

def retrieve_file(requested_file: str) -> Path:
    """
    Retrieves a file from the predefined download directory.
    
    Args:
        requested_file: str, the file requested by the user for download
        
    Returns:
        Path: The complete file path to the requested file
        
    Raises:
        FileNotFoundError: If the requested file is not found in the directory
        PermissionError: If the requested file is outside the allowed download directory
        Exception: For any other error conditions
    """
    # Resolve the requested file path relative to the download directory
    requested_path = (download_dir / requested_file).resolve()
    
    # Security check: ensure the resolved path is within the download directory
    try:
        requested_path.relative_to(download_dir.resolve())
    except ValueError:
        raise PermissionError("Access denied: requested file is outside the allowed download directory")
    
    # Check if the file exists and is a file (not a directory)
    if not requested_path.exists():
        raise FileNotFoundError(f"File not found: {requested_file}")
    
    if not requested_path.is_file():
        raise Exception(f"Requested path is not a file: {requested_file}")
    
    # Additional security: prevent hidden file access or other potential issues
    try:
        return requested_path
    except Exception as e:
        raise Exception(f"Error accessing file: {str(e)}")