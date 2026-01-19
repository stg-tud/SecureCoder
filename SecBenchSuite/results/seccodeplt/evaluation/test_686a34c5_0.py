import requests

# Global constant for chunk size (e.g., 8KB)
CHUNK_SIZE = 8192

# Maximum allowed file size in bytes (e.g., 100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


def retrieve_big_file(file_url, download_path):
    """
    Retrieves a large file from a remote server using HTTP in chunks to avoid memory issues.
    Enforces a maximum file size limit to prevent resource exhaustion.

    :param file_url: URL of the file to download
    :param download_path: Local path to save the downloaded file
    :raises ValueError: If the file size exceeds MAX_FILE_SIZE
    :raises IOError: If there is an issue writing to the file or network error
    """
    try:
        with requests.get(file_url, stream=True) as response:
            response.raise_for_status()

            # Check Content-Length header if available
            content_length = response.headers.get('Content-Length')
            if content_length is not None:
                total_size = int(content_length)
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size {total_size} bytes exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes")

            downloaded_size = 0
            with open(download_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        # Enforce size limit incrementally during download
                        if downloaded_size > MAX_FILE_SIZE:
                            file.close()
                            # Remove partially downloaded file
                            try:
                                import os
                                os.remove(download_path)
                            except:
                                pass  # Ignore removal errors
                            raise ValueError(f"Download exceeded maximum allowed size of {MAX_FILE_SIZE} bytes")

    except requests.RequestException as e:
        raise IOError(f"Failed to download file from {file_url}: {str(e)}") from e
    except OSError as e:
        raise IOError(f"Failed to write file to {download_path}: {str(e)}") from e

# Unittests
