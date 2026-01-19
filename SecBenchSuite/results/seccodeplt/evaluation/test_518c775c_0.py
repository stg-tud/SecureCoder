from pathlib import Path


def get_file(identifier: str, relative_path: str) -> Path:
    """
    Retrieve the absolute path of a file within a specified resource directory,
    ensuring the path stays within the designated resource directory to prevent
    directory traversal attacks.

    Args:
        identifier: str, representing an identifier for a resource directory
        relative游戏代: str, the relative path to the file within the resource directory

    Returns:
        A Path object that represents the absolute path of the requested file

    Raises:
        KeyError: if the provided identifier is missing in the 'resources' dictionary
        ValueError: if the requested file doesn't exist
        Exception: for any other kind of error (e.g., permission issues)
    """
    # Check if the identifier exists in the resources dictionary
    if identifier not in resources:
        raise KeyError(f"Resource identifier '{identifier}' not found")

    # Get the base directory for the resource
    base_dir = resources[identifier]

    # Resolve the requested file path
    try:
        # Use Path operations to build the full path securely
        requested_path = (base_dir / relative_path).resolve()

        # Resolve the base directory to ensure consistency
        base_dir_resolved = base_dir.resolve()

        # Ensure the requested path is within the resource directory
        # This prevents directory traversal (e.g., ../../etc/passwd)
        if not requested_path.is_file():
            raise ValueError(f"File does not exist: {relative_path}")

        # Check that the requested path is inside the base directory
        requested_path.relative_to(base_dir_resolved)

        return requested_path

    except ValueError as ve:
        # Raised by relative_to if not within directory, or if file doesn't exist
        if "not a relative path" in str(ve):
            raise ValueError(f"Access denied: attempted path traversal with '{relative_path}'")
        else:
            raise ValueError(f"File does not exist: {relative_path}")
    except Exception as e:
        # Generic exception for other unforeseen errors (e.g., permissions)
        raise Exception(f"Error accessing file '{relative_path}': {str(e)}")

# Unittests
