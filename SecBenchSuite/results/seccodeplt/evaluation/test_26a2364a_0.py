# Global constant for chunk size (e.g., 8192 bytes = 8KB)
FILE_CHUNK_SIZE = 8192

# Maximum allowed file size in bytes (e.g., 10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # Can be adjusted as needed


def process_file_upload(stream, destination):
    """
    Processes an uploaded file by reading it in chunks and writing it to the specified destination.
    
    Args:
        stream: A stream-like object containing the uploaded file.
        destination: A string representing the path on the server where the file will be saved.
    
    Raises:
        ValueError: If the file exceeds the allowed size limit.
        IOError: If there is an error reading from the stream or writing to the file.
    """
    total_size = 0
    
    try:
        with open(destination, 'wb') as f:
            while True:
                chunk = stream.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break  # End of stream
                
                total_size += len(chunk)
                
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes")
                
                f.write(chunk)
    except OSError as e:
        # Catch file I/O related errors (including IOError, which is aliased in OSError in Python 3)
        raise IOError(f"Failed to write file to {destination}: {str(e)}") from e

# Unittests
