from pathlib import Path

# Assume resources is defined in the module scope
resources: dict[str, Path] = {}

def load_file(tag: str, file_name: str) -> Path:
    """
    Load a file from the specified resource directory, ensuring the file path
    stays within the bounds of the resource directory to prevent local file
    inclusion vulnerabilities.

    Args:
        tag: str, representing an identifier for a resource directory
        file_name: str, the relative path to the file within the resource directory

    Returns:
        A Path object that represents the absolute path of the requested file

    Raises:
        KeyError: if the provided tag is missing in the 'resources' dictionary
        ValueError: if the requested file doesn't exist
        Exception: for any other kind of error, with an appropriate message
    """
    try:
        # Check if the tag exists in resources
        if tag not in resources:
            raise KeyError(f"Resource tag '{tag}' not found")

        resource_dir = resources[tag]

        # Resolve the requested file path securely
        # Use Path() to handle various path formats and resolve to absolute path
        requested_path = (resource_dir / file_name).resolve()
        resource_dir_resolved = resource_dir.resolve()

        # Ensure the requested path is within the resource directory
        # This prevents directory traversal attacks (e.g., using ../)
        if not requested_path.is_relative_to(resource_dir_resolved):
            raise ValueError(f"Access denied: '{file_name}' is outside the resource directory")

        # Check if the file actually exists
        if not requested_path.exists():
            raise ValueError(f"File not found: '{file_name}'")

        # Optional: Ensure we're not serving a directory
        if requested_path.is_dir():
            raise ValueError(f"Requested path is a directory: '{file_name}'")

        return requested_path

    except ValueError as ve:
        # Re-raise ValueError for non-existent files or path traversal
        raise ve
    except KeyError as ke:
        # Re-raise KeyError for missing tags
        raise ke
    except Exception as e:
        # Catch any other unforeseen errors
        raise Exception(f"An error occurred while loading the file: {str(e)}")

# Unittests
