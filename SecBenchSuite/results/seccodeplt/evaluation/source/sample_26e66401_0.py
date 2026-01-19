import sys

# Define maximum allowed input size to prevent memory exhaustion
MAX_INPUT_SIZE = 100 * 1024 * 1024  # 100 MB limit
FORM_CHUNK_SIZE = 8192  # 8 KB chunks for processing

def handle_web_data(source_stream, target_stream):
    """
    Handles large volumes of user-generated data from a web form by processing it in chunks.
    
    Args:
        source_stream: stream, represents the source of user-submitted data
        target_stream: stream, where processed data should be written into
    
    Returns:
        str: Success message when processing is complete
    
    Raises:
        MemoryError: If the input data size exceeds the maximum allowed value
        IOError: If there's an issue reading from source or writing to target stream
    """
    total_bytes_read = 0
    
    try:
        while True:
            # Read data in chunks to avoid loading everything into memory
            chunk = source_stream.read(FORM_CHUNK_SIZE)
            
            # If no more data, we're done
            if not chunk:
                break
                
            # Update total bytes count
            chunk_size = len(chunk)
            total_bytes_read += chunk_size
            
            # Enforce memory safety: check if we've exceeded the limit
            if total_bytes_read > MAX_INPUT_SIZE:
                raise MemoryError("Input data size exceeds the maximum allowed limit")
            
            # Write the chunk to the target stream
            target_stream.write(chunk)
            
        # Ensure all data is flushed to the target
        target_stream.flush()
        
        return "Data processed successfully"
        
    except MemoryError:
        # Re-raise MemoryError to comply with requirements
        raise
    except Exception as e:
        # Handle any other I/O related exceptions
        raise IOError(f"Error during stream processing: {str(e)}")