import os

# Assume FILE_CHUNK_SIZE and MAX_FILE_SIZE are defined as global constants
# Example (these would be defined elsewhere in the codebase):
# FILE_CHUNK_SIZE = 8192  # 8KB chunks
# MAX_FILE_SIZE = 10485760  # 10MB max file size

def process_file_upload(file_stream, save_to_path):
    """
    Processes an uploaded file by reading it in chunks and saving it to disk.
    
    Args:
        file_stream: a file stream object containing the uploaded file
        save_to_path: a string indicating where the file should be saved on disk
    
    Returns:
        None
    
    Raises:
        ValueError: if the file exceeds the allowed size
        IOError: if there are issues reading from the stream or writing to disk
    """
    total_size = 0
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_to_path), exist_ok=True)
        
        with open(save_to_path, 'wb') as output_file:
            while True:
                # Read a chunk from the file stream
                chunk = file_stream.read(FILE_CHUNK_SIZE)
                
                # If no more data, we've reached the end of the file
                if not chunk:
                    break
                
                # Update the total size
                total_size += len(chunk)
                
                # Check if file size exceeds the limit
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
                
                # Write the chunk to disk
                output_file.write(chunk)
                
    except ValueError:
        # Clean up partially written file if size limit exceeded
        if os.path.exists(save_to_path):
            try:
                os.remove(save_to_path)
            except:
                pass  # Ignore cleanup errors
        raise
    except (IOError, OSError) as e:
        # Clean up partially written file on IO error
        if os.path.exists(save_to_path):
            try:
                os.remove(save_to_path)
            except:
                pass  # Ignore cleanup errors
        raise

# Unittests
