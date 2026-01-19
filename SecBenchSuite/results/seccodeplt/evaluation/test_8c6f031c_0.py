def save_user_file(content_stream, path_to_save):
    """
    Save an uploaded file from a stream to the server in chunks, enforcing a size limit.
    
    Args:
        content_stream: A stream-like object representing the uploaded file
        path_to_save: String specifying where to save the file on the server
    
    Raises:
        ValueError: If the file being uploaded surpasses the specified size limit
        IOError: For any issues encountered during file manipulation
    
    Returns:
        None
    """
    MAX_FILE_SIZE = 100 * 1024 * 1024  # Example limit: 100MB (adjust as needed)
    total_size = 0
    
    try:
        with open(path_to_save, 'wb') as output_file:
            while True:
                chunk = content_stream.read(FILE_CHUNK_SIZE)
                
                # If no more data is returned, we've reached the end of the stream
                if not chunk:
                    break
                
                total_size += len(chunk)
                
                # Check if the file size exceeds the maximum allowed size
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes")
                
                output_file.write(chunk)
                
    except ValueError:
        # Re-raise size limit exceptions
        raise
    except IOError as e:
        # Handle any IO errors that occur during file operations
        raise IOError(f"Error saving file to {path_to_save}: {str(e)}") from e
    except Exception as e:
        # Handle any other unexpected exceptions during stream reading
        raise IOError(f"Error reading from content stream: {str(e)}") from e

# Unittests
