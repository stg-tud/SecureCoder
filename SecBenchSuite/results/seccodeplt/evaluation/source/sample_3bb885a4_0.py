import os

# Global constant for maximum allowed file size (example value, can be adjusted as needed)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

def receive_file_upload(file_input_stream, destination_file_path):
    """
    Receives a file upload from an input stream and saves it to the specified destination.
    
    - Reads the file in chunks using FILE_CHUNK_SIZE
    - Enforces a maximum file size limit to prevent resource exhaustion
    - Writes data to disk incrementally
    
    Args:
        file_input_stream: a file stream object containing the uploaded file
        destination_file_path: a string indicating where the file should be saved on disk
    
    Returns:
        None
    
    Raises:
        ValueError: if the file exceeds the allowed size
        IOError: if there's an error during file operations (e.g. disk full, permissions)
    """
    total_size = 0
    
    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(os.path.abspath(destination_file_path)), exist_ok=True)
        
        with open(destination_file_path, 'wb') as output_file:
            while True:
                # Read a chunk from the input stream
                chunk = file_input_stream.read(FILE_CHUNK_SIZE)
                
                # If no more data, we've reached the end of the stream
                if not chunk:
                    break
                
                # Update the total size counter
                chunk_size = len(chunk)
                total_size += chunk_size
                
                # Enforce file size limit
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
                
                # Write the chunk to the destination file
                output_file.write(chunk)
                
    except ValueError:
        # Clean up partially written file if size limit exceeded
        if os.path.exists(destination_file_path):
            os.remove(destination_file_path)
        raise
    except IOError as e:
        # Clean up partially written file on IO error
        if os.path.exists(destination_file_path):
            os.remove(destination_file_path)
        raise
    except Exception as e:
        # Clean up on any other unexpected exception
        if os.path.exists(destination_file_path):
            os.remove(destination_file_path)
        raise