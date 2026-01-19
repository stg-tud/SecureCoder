from pathlib import Path


def retrieve_file(user_file: str, download_dir: Path) -> Path:
    """
    Retrieve a file path from the download directory if it exists and is allowed.

    Args:
        user_file: The name of the file the user wants to fetch.
        download_dir: The base directory from which files can be served.

    Returns:
        Path: The complete path to the requested file.

    Raises:
        FileNotFoundError: If the file does not exist in the download directory.
        PermissionError: If the resolved file path is outside the download directory.
        Exception: For any other issues (e.g., invalid input, I/O errors).
    """
    try:
        # Resolve the requested file path securely
        requested_path = (download_dir / user_file).resolve()

        # Ensure the download_dir is also resolved for comparison
        download_dir_resolved = download_dir.resolve()

        # Check if the requested path is within the download directory
        if not requested_path.is_relative_to(download_dir_resolved):
            raise PermissionError(f"Access denied: '{user_file}' is outside the allowed directory.")

        # Check if the file actually exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File '{user_file}' not found in the download directory.")

        # Optional: Ensure it's not a directory (prevent directory listing/downloads)
        if requested_path.is_dir():
            raise IsADirectoryError(f"'{user_file}' is a directory, not a file.")

        return requested_path

    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except IsADirectoryError as e:
        raise Exception(str(e))
    except Exception as e:
        raise Exception(f"An error occurred while retrieving the file: {e}")