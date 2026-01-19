import requests
import os

# Predefined globally
CHUNK_SIZE = 8192  # 8KB chunks
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB maximum (adjust as needed)

def acquire_large_data(source_link: str, target_path: str) -> None:
    """
    Fetches a large file from the web using an HTTP request and downloads it in chunks
    to avoid loading the entire file into memory. Enforces a maximum file size to prevent
    resource exhaustion.

    Args:
        source_link (str): The source URL of the file to be downloaded.
        target_path (str): The local path where the downloaded file should be saved.

    Raises:
        ValueError: If the downloaded file surpasses the allowed size threshold.
        IOError: If there are issues with file handling or disk operations.
        requests.exceptions.RequestException: If there's an issue with the HTTP request.

    Returns:
        None; the file is written directly to local disk storage.
    """
    try:
        with requests.get(source_link, stream=True, timeout=30) as response:
            response.raise_for_status()
            
            # Try to get content length from headers
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                raise ValueError(f"File too large: {content_length} bytes exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
            
            total_size = 0
            
            # Ensure the target directory exists
            os.makedirs(os.path.dirname(os.path.abspath(target_path)) if os.path.dirname(target_path) else '.', exist_ok=True)
            
            with open(target_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        total_size += len(chunk)
                        
                        if total_size > MAX_FILE_SIZE:
                            # Remove partially downloaded file
                            try:
                                os.remove(target_path)
                            except:
                                pass  # Ignore removal errors
                            raise ValueError(f"Downloaded data exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
                            
                        try:
                            file.write(chunk)
                        except OSError as e:
                            raise IOError(f"Failed to write data to file: {e}")
                            
    except requests.exceptions.RequestException as e:
        raise IOError(f"Failed to download file from {source_link}: {e}")
    except OSError as e:
        raise IOError(f"Failed to create or access file at {target_path}: {e}")