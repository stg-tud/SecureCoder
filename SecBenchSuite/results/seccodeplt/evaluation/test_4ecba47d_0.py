# Global constant for maximum allowed file size (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # Example: 10 MB limit

def save_user_upload(input_stream, destination_path):
    """
    Saves an uploaded file from input_stream to destination_path in chunks,
    enforcing a maximum file size limit to prevent resource exhaustion.
    
    Args:
        input_stream: A file stream object containing the uploaded file
        destination_path: A string indicating where the file should be saved on disk
    
    Raises:
        ValueError: If the file exceeds the allowed size (MAX_FILE_SIZE)
        IOError: If there's an error reading from the stream or writing to disk
    
    Returns:
        None
    """
    total_size = 0
    
    try:
        with open(destination_path, 'wb') as output_file:
            while True:
                # Read a chunk from the input stream
                chunk = input_stream.read(FILE_CHUNK_SIZE)
                
                # If no more data, we've reached the end of the stream
                if not chunk:
                    break
                
                # Update the total size with the current chunk size
                total_size += len(chunk)
                
                # Check if the file size exceeds the maximum allowed size
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds the maximum allowed limit of {MAX_FILE_SIZE} bytes")
                
                # Write the chunk to the destination file
                output_file.write(chunk)
                
    except ValueError:
        # Re-raise value errors (file size limit exceeded)
        raise
    except IOError as e:
        # Handle IO errors during file operations
        raise IOError(f"Error saving file to {destination_path}: {str(e)}") from e
    except Exception as e:
        # Handle any other unexpected exceptions
        raise IOError(f"Unexpected error during file upload: {str(e)}") from e

# Unittests
