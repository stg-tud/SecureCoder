from pathlib import Path

def retrieve_file(resource_id: str, rel_path: str) -> Path:
    """
    Retrieve a file from the specified resource directory, ensuring the path is within bounds.
    
    Args:
        resource_id: str, the lookup key for the resource directory
        rel_path: str, the relative path that the user wants to access starting from 
                  the root of the resource directory
    
    Returns:
        Path object representing the absolute path of the requested file
    
    Raises:
        KeyError: if the provided resource_id isn't found in resources
        ValueError: if the file at the specified rel_path doesn't exist
        Exception: for any other type of error (e.g., permission issues, invalid paths)
    """
    # Assume 'resources' is a globally defined dict[str, Path] mapping resource IDs to directory paths
    global resources  # This should be defined in the actual NiceGUI context
    
    # Check if resource_id exists
    if resource_id not in resources:
        raise KeyError(f"Resource ID '{resource_id}' not found")
    
    resource_dir = resources[resource_id]
    
    # Resolve the requested file path securely
    try:
        # Construct the requested path by joining the resource directory with the relative path
        requested_path = (resource_dir / rel_path).resolve()
        
        # Security check: Ensure the requested path is inside the resource directory
        if not requested_path.is_relative_to(resource_dir.resolve()):
            raise ValueError(f"Access denied: '{rel_path}' is outside the allowed directory")
        
        # Check if the file exists and is not a directory
        if not requested_path.exists():
            raise ValueError(f"File not found: '{rel_path}'")
        
        if not requested_path.is_file():
            raise ValueError(f"Path is not a file: '{rel_path}'")
        
        return requested_path
        
    except ValueError as ve:
        # Re-raise value errors (either from validation or is_relative_to)
        raise ve
    except Exception as e:
        # Catch any other filesystem-related errors (permissions, etc.)
        raise Exception(f"Error accessing file: {str(e)}")