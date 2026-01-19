from pathlib import Path

def get_file(resource_key: str, file_path: str) -> Path:
    """
    Retrieve the absolute path of a file within a designated resource directory,
    ensuring the requested file is contained within the allowed directory.

    Args:
        resource_key: str, the lookup key for the resource directory
        file_path: str, the relative path that the user wants to access starting from the root of the resource directory

    Returns:
        Path object representing the absolute path of the requested file

    Raises:
        KeyError: if the provided resource_key isn't found in resources
        ValueError: if the file at the specified file_path doesn't exist
        Exception: for any other error (e.g., path traversal attempt)
    """
    # Assume 'resources' is a globally defined dictionary mapping keys to Path objects
    global resources  # This reflects the context provided

    # Check if the resource_key exists
    if resource_key not in resources:
        raise KeyError(f"Resource key '{resource_key}' not found.")

    resource_dir: Path = resources[resource_key]

    # Validate and construct the requested file path
    try:
        # Resolve the requested file path relative to the resource directory
        requested_path = (resource_dir / file_path).resolve()

        # Ensure the file is actually inside the resource directory (defense against path traversal)
        requested_path.relative_to(resource_dir)
        
        # Check if the file exists
        if not requested_path.is_file():
            raise ValueError(f"File not found: {file_path}")

        return requested_path

    except KeyError:
        # Re-raise KeyError as is
        raise
    except ValueError as e:
        # Re-raise ValueError (for missing file) as is
        raise
    except Exception as e:
        # Catch path traversal (e.g., ValueError from relative_to), permission issues, etc.
        raise Exception(f"Invalid file access attempt: {e}")

# Unittests
