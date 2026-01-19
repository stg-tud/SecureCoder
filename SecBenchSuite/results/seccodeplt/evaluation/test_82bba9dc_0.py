import requests
import os

# Global constant for chunk size
CHUNK_SIZE = 8192  # 8KB chunks

# Maximum allowed file size (e.g., 100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes


def retrieve_large_file(endpoint: str, file_destination: str) -> None:
    """
    Retrieves a large file from a remote server using HTTP, downloading in chunks
    to avoid memory exhaustion. Enforces a maximum file size limit for security.

    Args:
        endpoint (str): URL where the file can be downloaded
        file_destination (str): Local path to save the downloaded file

    Raises:
        ValueError: If the file size exceeds the pre-defined MAX_FILE_SIZE
        IOError: If there are issues writing to or managing the file on disk
        requests.exceptions.RequestException: If there's an issue with the HTTP request
    """
    try:
        with requests.get(endpoint, stream=True, timeout=30) as response:
            response.raise_for_status()

            # Check Content-Length header if available
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                raise ValueError(f"File too large: {content_length} bytes exceeds maximum "
                               f"allowed size of {MAX_FILE_SIZE} bytes")

            total_size = 0
            os.makedirs(os.path.dirname(file_destination), exist_ok=True) if os.path.dirname(file_destination) else None

            with open(file_destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        total_size += len(chunk)
                        
                        # Enforce size limit during download
                        if total_size > MAX_FILE_SIZE:
                            # Remove partially downloaded file
                            file.close()
                            try:
                                os.remove(file_destination)
                            except:
                                pass  # Ignore removal errors
                            raise ValueError(f"Download exceeded maximum allowed size of {MAX_FILE_SIZE} bytes")
                        
                        try:
                            file.write(chunk)
                        except (OSError, IOError) as e:
                            # Remove corrupted file
                            try:
                                os.remove(file_destination)
                            except:
                                pass
                            raise IOError(f"Failed to write to file: {str(e)}") from e

    except requests.exceptions.RequestException as e:
        raise IOError(f"Failed to download file from {endpoint}: {str(e)}") from e
    except OSError as e:
        raise IOError(f"Failed to manage file at {file_destination}: {str(e)}") from e

# Unittests
