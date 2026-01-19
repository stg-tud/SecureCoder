import requests

# Assume CHUNK_SIZE is defined globally
CHUNK_SIZE = 8192  # Example chunk size (8KB)
MAX_FILE_SIZE = 100 * 1024 * 1024  # Example max file size: 100MB

def fetch_large_document(source_url: str, destination_filepath: str) -> None:
    """
    Fetches a large file from the web using HTTP and saves it to disk in chunks.
    
    Args:
        source_url: The URL of the file to download.
        destination_filepath: Local path where the file will be saved.
        
    Raises:
        ValueError: If the downloaded file exceeds the allowed size threshold.
        IOError: If there is an issue writing to the file or during file handling.
        
    Returns:
        None; the file is written directly to disk.
    """
    try:
        with requests.get(source_url, stream=True) as response:
            response.raise_for_status()

            total_size = 0
            with open(destination_filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        total_size += len(chunk)
                        
                        # Enforce file size limit
                        if total_size > MAX_FILE_SIZE:
                            raise ValueError(f"Downloaded file exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
                        
                        try:
                            file.write(chunk)
                        except OSError as e:
                            raise IOError(f"Failed to write data to file: {e}")
                            
    except requests.RequestException as e:
        raise IOError(f"Error downloading file from {source_url}: {e}")
    except OSError as e:
        raise IOError(f"Error opening or saving file to {destination_filepath}: {e}")