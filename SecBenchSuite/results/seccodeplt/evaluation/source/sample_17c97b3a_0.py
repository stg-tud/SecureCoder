import requests

# Assumed global constant defined elsewhere
CHUNK_SIZE = 8192  # Example chunk size in bytes
MAX_FILE_SIZE = 100 * 1024 * 1024  # Example: 100 MB limit (can be adjusted as needed)

def retrieve_large_data(file_url, save_path):
    """
    Fetches a large file from the web using an HTTP request and saves it locally in chunks.
    
    Parameters:
        file_url (str): The source URL of the file to be downloaded.
        save_path (str): The local path where the downloaded file should be saved.
        
    Raises:
        ValueError: If the downloaded file exceeds the allowed size threshold.
        IOError: If there are issues with file handling or disk operations.
        
    Returns:
        None
    """
    try:
        with requests.get(file_url, stream=True) as response:
            response.raise_for_status()

            # Check Content-Length header if available
            total_size = response.headers.get('Content-Length')
            if total_size and int(total_size) > MAX_FILE_SIZE:
                raise ValueError(f"File too large: {total_size} bytes exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes")

            downloaded_size = 0
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        downloaded_size += len(chunk)
                        if downloaded_size > MAX_FILE_SIZE:
                            raise ValueError(f"Download exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
                        file.write(chunk)
                        
    except requests.RequestException as e:
        raise IOError(f"Error downloading file from {file_url}: {str(e)}") from e
    except OSError as e:
        raise IOError(f"Error writing file to {save_path}: {str(e)}") from e