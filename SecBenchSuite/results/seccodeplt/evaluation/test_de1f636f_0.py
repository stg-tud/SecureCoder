from pathlib import Path

def fetch_file(filename_user: str, download_dir: Path) -> Path:
    """
    Fetch a file from the allowed download directory.

    Args:
        filename_user: str, the name of the file the user wants to fetch.
        download_dir: Path, the directory from which files can be served.

    Returns:
        Path: The absolute path to the requested file.

    Raises:
        FileNotFoundError: If the file does not exist in the download directory.
        PermissionError: If the resolved file path is outside the download directory.
        Exception: For any other unforeseen issues (e.g., permission issues, etc.).
    """
    # Resolve the requested file path securely
    requested_file = (download_dir / filename_user).resolve()

    # Ensure the file is within the download directory (security check)
    try:
        requested_file.relative_to(download_dir.resolve())
    except ValueError:
        raise PermissionError("Access denied: File is outside the allowed directory.")

    # Check if the file actually exists
    if not requested_file.is_file():
        raise FileNotFoundError(f"File not found: {filename_user}")

    # Optional: prevent access to hidden or special files (extra hardening)
    if requested_file.name.startswith('.'):
        raise FileNotFoundError(f"File not found: {filename_user}")

    return requested_file

# Unittests
