import requests

# Global constant for chunk size
CHUNK_SIZE = 8192

# Maximum allowable file size in bytes (e.g., 100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


def download_large_file(url: str, local_filepath: str) -> None:
    """
    Downloads a large file from a remote server in chunks and saves it locally.
    
    Args:
        url: The URL of the file to download.
        local_filepath: The local path where the file should be saved.
    
    Raises:
        ValueError: If the file size exceeds the maximum allowable size.
        IOError: If there is an issue writing to the file or during the download.
    """
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            # Check Content-Length header if available
            content_length = response.headers.get('Content-Length')
            if content_length is not None:
                total_size = int(content_length)
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size {total_size} bytes exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.")

            downloaded_size = 0
            
            with open(local_filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        downloaded_size += len(chunk)
                        
                        # Enforce download size limit during streaming
                        if downloaded_size > MAX_FILE_SIZE:
                            raise ValueError(f"Downloaded data exceeds maximum allowed size of {MAX_FILE_SIZE} bytes.")
                            
                        file.write(chunk)
                        
    except requests.exceptions.RequestException as e:
        raise IOError(f"Error downloading file: {e}") from e
    except OSError as e:
        raise IOError(f"Error writing file to disk: {e}") from e
    except ValueError:
        # Re-raise ValueError for size limit
        raise
    except Exception as e:
        raise IOError(f"Unexpected error during file download: {e}") from e

# Unittests
