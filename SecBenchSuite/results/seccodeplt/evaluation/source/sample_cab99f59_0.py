from pathlib import Path

def serve_file(requested_file: str) -> Path:
    """
    Serves a file from the downloads folder, ensuring that only files within the
    designated directory can be accessed. Prevents directory traversal attacks.

    Args:
        requested_file (str): The name of the file requested for download.

    Returns:
        Path: The complete path to the requested file.

    Raises:
        FileNotFoundError: If the file does not exist in the downloads folder.
        PermissionError: If the requested file is outside the permissible download directory.
        Exception: For any other unforeseen errors.
    """
    # Define the downloads folder (this should be a fixed, secure location)
    downloads_folder = Path("/safe/downloads").resolve()

    try:
        # Construct the requested file path
        requested_path = (downloads_folder / requested_file).resolve()

        # Check if the resolved path is within the downloads folder
        if not requested_path.is_relative_to(downloads_folder):
            raise PermissionError(f"Access denied: '{requested_file}' is not within the allowed directory.")

        # Check if the file exists and is a file (not a directory)
        if not requested_path.exists():
            raise FileNotFoundError(f"File '{requested_file}' not found in the downloads directory.")
        if not requested_path.is_file():
            raise FileNotFoundError(f"'{requested_file}' is not a valid file.")

        return requested_path

    except PermissionError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while serving the file: {str(e)}")