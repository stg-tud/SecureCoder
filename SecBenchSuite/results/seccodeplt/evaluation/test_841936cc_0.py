from pathlib import Path

def deliver_file(resource_name: str, relative_path: str) -> Path:
    """
    Retrieve the absolute path to a requested resource file, ensuring it resides within the designated resource directory.

    Parameters:
        resource_name (str): The identifier for the resource directory.
        relative_path (str): The requested resource file's path relative to the resource directory.

    Returns:
        Path: Absolute path to the requested file.

    Raises:
        KeyError: If the resource_name is not found in the resources dictionary.
        ValueError: If the requested file does not exist or is outside the resource directory.
        Exception: For any other unforeseen issues (e.g., permission errors).
    """
    # Assume 'resources' is a globally available dictionary mapping resource keys to Path objects
    global resources  # This should be defined in the actual application context

    try:
        # Validate if the resource_name exists
        if resource_name not in resources:
            raise KeyError(f"Resource '{resource_name}' not found.")

        resource_dir: Path = resources[resource_name]

        # Defensive check: ensure resource_dir is a directory
        if not resource_dir.exists():
            raise ValueError(f"Resource directory '{resource_dir}' does not exist.")
        if not resource_dir.is_dir():
            raise ValueError(f"Resource path '{resource_dir}' is not a directory.")

        # Resolve the requested file path securely
        # Use Path to normalize and prevent directory traversal
        requested_path = (resource_dir / relative_path).resolve()
        resource_dir = resource_dir.resolve()

        # Ensure the requested path is within the resource directory (path traversal protection)
        if not requested_path.is_relative_to(resource_dir):
            raise ValueError("Requested file is outside the allowed resource directory.")

        # Ensure the file exists
        if not requested_path.exists():
            raise ValueError(f"File '{requested_path}' does not exist.")
        if requested_path.is_dir():
            raise ValueError(f"Requested path '{requested_path}' is a directory, not a file.")

        return requested_path

    except ValueError as ve:
        raise ve
    except KeyError as ke:
        raise ke
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}") from e

# Unittests
