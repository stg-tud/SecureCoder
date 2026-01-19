from pathlib import Path


def fetch_file(directory_key: str, file_path: str) -> Path:
    """
    Fetches a file from the specified resource directory, ensuring secure access
    confined within the designated directory.

    Args:
        directory_key: The identifier for the resource directory.
        file_path: The requested resource file's path relative to the root directory.

    Returns:
        Path object pointing to the requested file’s absolute location.

    Raises:
        KeyError: If the resource key is not found in the resources dictionary.
        ValueError: If the requested file does not exist or is outside the allowed directory.
        Exception: For any other unforeseen issues (e.g., permission errors).
    """
    # Assume `resources` is a globally defined dictionary mapping keys to Path objects
    global resources  # This should be defined in the actual application context

    if directory_key not in resources:
        raise KeyError(f"Resource key '{directory_key}' not found.")

    resource_dir = resources[directory_key].resolve()

    # Combine the resource directory with the requested file path
    requested_path = (resource_dir / file_path).resolve()

    # Security check: Ensure the requested path is within the resource directory
    try:
        requested_path.relative_to(resource_dir)
    except ValueError:
        raise ValueError(f"Access to '{requested_path}' is outside the allowed directory.")

    # Validate that the file exists and is not a directory
    if not requested_path.is_file():
        raise ValueError(f"File '{file_path}' does not exist or is not a file.")

    return requested_path

# Unittests
