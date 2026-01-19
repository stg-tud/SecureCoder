# Global constant for maximum allowed file size (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # Example: 10 MB limit

# Global constant for chunk size when reading the file
FILE_CHUNK_SIZE = 8192  # 8 KB per chunk

def upload_user_file(file_input_stream, output_path):
    """
    Uploads a user file from the input stream and saves it to the specified output path.
    
    Arguments:
    - file_input_stream: a stream-like object containing the uploaded file
    - output_path: a string representing the path on the server where the file will be saved
    
    Raises:
    - ValueError: if the file exceeds the allowed size limit
    - IOError: for file operation problems (e.g., permission denied, disk full)
    
    Security Policy:
    - Enforces a maximum file size limit to prevent memory exhaustion.
    - Processes the file in chunks to control memory usage.
    """
    total_size = 0
    
    try:
        with open(output_path, 'wb') as output_file:
            while True:
                chunk = file_input_stream.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break  # End of stream
                    
                total_size += len(chunk)
                
                # Check if file size exceeds the maximum allowed
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE} bytes")
                
                output_file.write(chunk)
                
    except ValueError:
        # Re-raise ValueError if it's about file size
        raise
    except Exception as e:
        # Catch other file I/O related errors and raise as IOError
        raise IOError(f"Error writing file to {output_path}: {str(e)}") from e