from pathlib import Path

resources: dict[str, Path] = {}

def serve_file(key: str, path: str) -> Path:
    """
    Serve a file from the specified resource key and relative path.
    
    Args:
        key: str, the key of the resource
        path: str, the path that the user wants to access relative to the resource root
    
    Returns:
        Path: the real path of the file
    
    Raises:
        KeyError: if the key is not in the resources
        ValueError: if the file does not exist
        Exception: if any other exception occurs
    """
    try:
        # Check if the key exists in resources
        if key not in resources:
            raise KeyError(f"Resource key '{key}' not found")
        
        resource_path = resources[key]
        
        # Resolve the requested file path relative to the resource root
        requested_path = (resource_path / path).resolve()
        
        # Security check: Ensure the requested path is under the resource path
        # This prevents directory traversal attacks
        if not requested_path.is_relative_to(resource_path.resolve()):
            raise ValueError(f"Access denied: '{path}' is outside the allowed resource directory")
        
        # Check if the file exists
        if not requested_path.exists():
            raise ValueError(f"File not found: '{path}'")
        
        return requested_path
        
    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while serving file: {str(e)}")