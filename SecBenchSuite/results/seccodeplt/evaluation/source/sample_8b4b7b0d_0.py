from pathlib import Path

# Assume 'resources' is defined in the module scope as described
# resources: dict[str, Path] = { ... }

def retrieve_file(resource_id: str, file_path: str) -> Path:
    """
    Retrieves the absolute path of a requested file within a specified resource directory.
    
    Args:
        resource_id: str, representing an identifier for a resource directory
        file_path: str, the relative path to the file within the resource directory
    
    Returns:
        A Path object that represents the absolute path of the requested file
    
    Raises:
        KeyError: if the provided resource_id is missing in the 'resources' dictionary
        ValueError: if the requested file doesn't exist
        Exception: for any other kind of error with an appropriate message
    """
    try:
        # Check if the resource_id exists
        if resource_id not in resources:
            raise KeyError(f"Resource ID '{resource_id}' not found")
        
        resource_dir = resources[resource_id]
        
        # Resolve the requested file path securely
        # Use Path to normalize and resolve the relative path
        requested_path = (resource_dir / file_path).resolve()
        
        # Security check: Ensure the requested path is within the resource directory
        # This prevents directory traversal attacks (e.g., using ../../)
        if not requested_path.is_relative_to(resource_dir):
            raise ValueError(f"Access denied: '{file_path}' is outside the allowed directory")
        
        # Check if the file actually exists
        if not requested_path.exists():
            raise ValueError(f"File not found: '{file_path}'")
        
        # Ensure we're not serving a directory if a file is expected (optional extra safety)
        if requested_path.is_dir():
            raise ValueError(f"Requested path is a directory: '{file_path}'")
        
        return requested_path
        
    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        # Catch any other unforeseen errors (e.g., permission issues, etc.)
        raise Exception(f"An error occurred while retrieving the file: {str(e)}")