import os
from typing import IO

# Global configuration
FILE_CHUNK_SIZE = 8192  # Size of each chunk to read (e.g., 8KB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # Maximum allowed file size (e.g., 10MB)

def handle_file_upload(upload_stream: IO[bytes], target_filepath: str) -> None:
    """
    Handles file upload by streaming data in chunks to prevent excessive memory usage.
    
    Args:
        upload_stream: The input stream containing the uploaded file (supports read()).
        target_filepath: The path where the file should be saved.
        
    Raises:
        ValueError: If the uploaded file exceeds the maximum allowed size.
        IOError: If there is an issue reading from the stream or writing to the file.
    """
    total_size = 0
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
        
        with open(target_filepath, 'wb') as output_file:
            while True:
                chunk = upload_stream.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break  # End of stream
                
                total_size += len(chunk)
                
                # Enforce file size limit
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE} bytes")
                
                output_file.write(chunk)
                
    except OSError as e:
        # Handle file system or I/O related errors
        raise IOError(f"Failed to write file to {target_filepath}: {str(e)}") from e
    except ValueError:
        # Re-raise size limit error
        raise
    except Exception as e:
        # Catch any other stream-related issues
        raise IOError(f"Error during file upload: {str(e)}") from e