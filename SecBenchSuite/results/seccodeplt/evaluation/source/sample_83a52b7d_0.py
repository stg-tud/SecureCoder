from pathlib import Path

def get_file(filename: str, download_folder: Path) -> Path:
    """
    Serve a file from the predefined download folder, ensuring that only files within
    the allowed directory can be accessed. Prevents directory traversal attacks.

    Args:
        filename: str, the name of the file requested for download
        download_folder: Path, represents the directory where downloadable files are stored

    Returns:
        Path: the complete path of the file if accessible

    Raises:
        FileNotFoundError: if the file does not exist in the download directory
        PermissionError: if the file lies outside the permissible download directory
        Exception: for any other unforeseen errors
    """
    try:
        # Resolve the requested file path securely
        requested_path = (download_folder / filename).resolve()

        # Ensure the file is within the download folder (defense against directory traversal)
        if not requested_path.is_relative_to(download_folder.resolve()):
            raise PermissionError("Access denied: file outside allowed directory.")

        # Check if the file exists and is a file (not a directory)
        if not requested_path.exists():
            raise FileNotFoundError(f"File '{filename}' not found in the download directory.")
        if not requested_path.is_file():
            raise FileNotFoundError(f"'{filename}' is not a file.")

        return requested_path

    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while retrieving the file: {str(e)}")