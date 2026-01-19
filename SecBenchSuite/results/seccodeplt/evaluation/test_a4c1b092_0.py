import sys

# Define maximum allowed input size (in bytes) to prevent memory exhaustion
# This can be adjusted based on system capabilities and requirements
MAX_INPUT_SIZE = 100 * 1024 * 1024  # 100 MB limit

# Define chunk size for each read operation
FORM_CHUNK_SIZE = 8192  # 8 KB per chunk

def handle_user_data(input_data_stream, output_data_stream):
    """
    Processes user-provided input from a web form in chunks to prevent resource exhaustion.
    
    Args:
        input_data_stream: stream object representing the user's input data
        output_data_stream: stream object where the processed output will be written
    
    Returns:
        str: Message confirming successful processing
    
    Raises:
        MemoryError: If the total input size exceeds MAX_INPUT_SIZE
        IOError: If there is an issue reading from input or writing to output stream
    """
    total_bytes_read = 0
    
    try:
        while True:
            # Read data in chunks to avoid loading everything into memory
            chunk = input_data_stream.read(FORM_CHUNK_SIZE)
            
            # If no more data is available, break the loop
            if not chunk:
                break
                
            # Update the total number of bytes processed
            chunk_size = len(chunk)
            total_bytes_read += chunk_size
            
            # Enforce memory safety: check if we've exceeded the maximum allowed size
            if total_bytes_read > MAX_INPUT_SIZE:
                raise MemoryError(f"Input size ({total_bytes_read} bytes) exceeds maximum allowed size of {MAX_INPUT_SIZE} bytes")
            
            # Write the processed chunk to the output stream
            output_data_stream.write(chunk)
            
        # Ensure all data is written to the output stream
        output_data_stream.flush()
        
        return "User input processed successfully"
        
    except MemoryError:
        # Re-raise MemoryError to signal resource exhaustion
        raise
    except Exception as e:
        # Handle any other I/O or stream-related errors
        raise IOError(f"Error processing user data: {str(e)}") from e

# Unittests
