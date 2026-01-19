import requests
import os

# Global CHUNK_SIZE (assumed to be defined as per context)
# Example: CHUNK_SIZE = 8192  # 8KB chunks

# Predefined file size limit (e.g., 100MB limit - this should be set according to policy)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB limit

def transfer_large_file(uri, destination_path):
    """
    Retrieves a large file from a remote server using HTTP and saves it in chunks
    to avoid excessive memory usage. Enforces a maximum file size limit to prevent
    resource exhaustion.

    :param uri: string, the URL to access the file
    :param destination_path: string, the path where the file will be saved
    :raises ValueError: if the file size exceeds MAX_FILE_SIZE
    :raises IOError: if there is an issue with disk I/O operations
    """
    try:
        response = requests.get(uri, stream=True)
        response.raise_for_status()

        # Check content-length header if available
        content_length = response.headers.get('Content-Length')
        if content_length is not None:
            file_size = int(content_length)
            if file_size > MAX_FILE_SIZE:
                raise ValueError(f"File size {file_size} bytes exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.")

        # Ensure the destination directory exists
        destination_dir = os.path.dirname(destination_path)
        if destination_dir and not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        downloaded_size = 0
        try:
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Double-check size during download in case Content-Length was missing or inaccurate
                        if downloaded_size > MAX_FILE_SIZE:
                            f.close()
                            os.remove(destination_path)  # Clean up partial file
                            raise ValueError(f"Download exceeded maximum allowed file size of {MAX_FILE_SIZE} bytes.")
        except PermissionError as e:
            raise IOError(f"Permission denied when writing to file: {destination_path}") from e
        except OSError as e:
            raise IOError(f"Disk I/O error occurred: {e}") from e

    except requests.RequestException as e:
        raise IOError(f"Error downloading file from {uri}: {e}") from e