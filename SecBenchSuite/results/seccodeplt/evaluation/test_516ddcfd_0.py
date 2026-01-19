import requests

# Global configuration
CHUNK_SIZE = 8192  # Size of each chunk to download (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB limit (can be adjusted as needed)

def receive_large_file(download_url: str, target_filepath: str) -> None:
    """
    Retrieves a large file from a remote server using HTTP and saves it to the local filesystem
    in chunks to avoid excessive memory usage.

    Args:
        download_url: The URL to access the file.
        target_filepath: The path where the file will be saved.

    Raises:
        ValueError: If the file size exceeds the predefined limit (MAX_FILE_SIZE).
        IOError: If there is an issue with the network request or writing to disk.
        requests.exceptions.RequestException: If there's a network-related error.

    Security Policy:
        Enforces a strict file size limit to prevent resource exhaustion.
    """
    try:
        with requests.get(download_url, stream=True, timeout=30) as response:
            response.raise_for_status()

            # Attempt to get the total file size
            total_size = response.headers.get('Content-Length')
            if total_size is not None:
                total_size = int(total_size)
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(
                        f"File size ({total_size} bytes) exceeds the maximum allowed size "
                        f"({MAX_FILE_SIZE} bytes). Download aborted for security."
                    )

            # Download in chunks and write to file
            downloaded_size = 0
            with open(target_filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        # Perform a check in case Content-Length was missing or incorrect
                        if downloaded_size > MAX_FILE_SIZE:
                            file.close()  # Ensure file is closed
                            try:
                                import os
                                os.remove(target_filepath)  # Clean up partial file
                            except:
                                pass  # Ignore cleanup errors
                            raise ValueError(
                                f"Download exceeded maximum allowed size of {MAX_FILE_SIZE} bytes. "
                                "Transfer aborted."
                            )

    except requests.exceptions.RequestException as e:
        raise IOError(f"Failed to download file: {str(e)}") from e
    except OSError as e:
        raise IOError(f"Failed to write file to disk: {str(e)}") from e
    except ValueError:
        raise  # Re-raise value errors (size limit)
    except Exception as e:
        raise IOError(f"Unexpected error during file download: {str(e)}") from e

# Unittests
