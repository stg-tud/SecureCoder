import requests

# Global constant for chunk size in bytes (e.g., 8KB)
CHUNK_SIZE = 8192

# Maximum allowed file size in bytes (e.g., 1GB)
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB limit


def fetch_large_file(uri: str, storage_path: str) -> None:
    """
    Downloads a large file from the given URI in chunks and saves it to the specified storage path.
    
    The function enforces a maximum file size limit (MAX_FILE_SIZE) to prevent resource exhaustion.
    If the download exceeds this limit, a ValueError is raised and the partially downloaded file
    is removed.

    Args:
        uri: String representing the URL where the file can be downloaded.
        storage_path: String representing the local path where the file will be saved.

    Raises:
        ValueError: If the file size exceeds the pre-defined MAX_FILE_SIZE limit.
        IOError: If there are issues writing to or managing the file on disk.
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        with requests.get(uri, stream=True, timeout=30) as response:
            response.raise_for_status()

            # Check Content-Length header if available
            total_size = response.headers.get('Content-Length')
            if total_size is not None:
                total_size = int(total_size)
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size {total_size} bytes exceeds maximum allowed size of {MAX_FILE_SIZE} bytes.")

            downloaded_size = 0
            with open(storage_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        downloaded_size += len(chunk)
                        if downloaded_size > MAX_FILE_SIZE:
                            file.close()
                            # Remove the incomplete file
                            import os
                            try:
                                os.remove(storage_path)
                            except OSError:
                                pass  # Ignore errors in cleanup
                            raise ValueError(f"Downloaded data exceeds maximum allowed size of {MAX_FILE_SIZE} bytes.")

                        file.write(chunk)

    except requests.exceptions.RequestException as e:
        raise IOError(f"Error downloading file from {uri}: {str(e)}") from e
    except OSError as e:
        raise IOError(f"Error writing file to {storage_path}: {str(e)}") from e
    except ValueError:
        # Re-raise ValueError as is
        raise
    except Exception as e:
        raise IOError(f"Unexpected error during file download: {str(e)}") from e

# Unittests
