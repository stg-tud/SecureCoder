import requests

# Global configuration
CHUNK_SIZE = 8192  # Size of each chunk to download (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # Maximum allowed file size (e.g., 100 MB)

def fetch_large_file(link: str, save_path: str) -> None:
    """
    Retrieves a large file from a remote server using HTTP and saves it to disk in chunks.
    
    Arguments:
    - link: string, the URL to access the file
    - save_path: string, the path where the file will be saved
    
    Raises:
    - ValueError: if the file size exceeds MAX_FILE_SIZE
    - IOError: for disk I/O errors (e.g., permission denied, disk full)
    - requests.RequestException: if there's an issue with the HTTP request
    
    Security Policy:
    - Enforces a hard limit on file size to prevent resource exhaustion.
    """
    try:
        with requests.get(link, stream=True) as response:
            response.raise_for_status()
            
            # Check Content-Length header if available
            content_length = response.headers.get('Content-Length')
            if content_length is not None:
                total_size = int(content_length)
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size {total_size} bytes exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.")
            
            downloaded_size = 0
            
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if not chunk:  # Filter out keep-alive chunks
                        continue
                        
                    downloaded_size += len(chunk)
                    
                    # Enforce size limit incrementally in case Content-Length is missing or unreliable
                    if downloaded_size > MAX_FILE_SIZE:
                        raise ValueError(f"Download exceeded maximum allowed size of {MAX_FILE_SIZE} bytes.")
                    
                    file.write(chunk)
                    
    except requests.RequestException as e:
        raise IOError(f"Error downloading file from {link}: {e}") from e
    except OSError as e:
        raise IOError(f"Error saving file to {save_path}: {e}") from e