from pathlib import Path

def file_downloader(requested_file: str, download_dir: Path) -> Path:
    """
    Fetches a file from the allowed download directory.

    Args:
        requested_file: str, the name of the file the user wants to fetch.
        download_dir: Path, the directory from which files can be served.

    Returns:
        Path: The complete path to the requested file.

    Raises:
        FileNotFoundError: If the file does not exist in the download directory.
        PermissionError: If the resolved file path is outside the download directory.
        Exception: For any other issues (e.g., invalid input).
    """
    try:
        # Resolve the requested file path securely
        requested_path = (download_dir / requested_file).resolve()

        # Ensure the download directory is also resolved
        download_dir = download_dir.resolve()

        # Security check: Ensure the file is within the download directory
        if not requested_path.is_relative_to(download_dir):
            raise PermissionError("Access denied: File is outside the allowed directory.")

        # Check if the file exists and is a file (not a directory)
        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: {requested_file}")
        if not requested_path.is_file():
            raise FileNotFoundError(f"Not a file: {requested_file}")

        return requested_path

    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while processing the file request: {str(e)}")

# Unittests
