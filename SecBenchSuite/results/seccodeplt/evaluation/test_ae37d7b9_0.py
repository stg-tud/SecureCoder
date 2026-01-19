import io

# Define the chunk size for reading input streams
FORM_CHUNK_SIZE = 8192  # 8KB chunks

# Define a safe limit for total input size (e.g., 100MB)
SAFE_INPUT_LIMIT = 100 * 1024 * 1024  # 100 MB


def manage_user_input(input_stream_data: io.IOBase, output_stream_data: io.IOBase):
    """
    Processes user-provided input from a web form in chunks to prevent excessive memory usage.
    
    Args:
        input_stream_data: Stream object representing the user's input data
        output_stream_data: Stream object where the processed output will be written
    
    Returns:
        str: Message confirming successful processing of the user input
    
    Raises:
        MemoryError: If the processed input size exceeds a predefined safe limit
        ValueError: If invalid stream objects are provided
    """
    if not hasattr(input_stream_data, 'read') or not callable(input_stream_data.read):
        raise ValueError("input_stream_data must be a readable stream object")
    
    if not hasattr(output_stream_data, 'write') or not callable(output_stream_data.write):
        raise ValueError("output_stream_data must be a writable stream object")

    total_bytes_read = 0

    try:
        while True:
            chunk = input_stream_data.read(FORM_CHUNK_SIZE)
            
            # Check if we've reached the end of the stream
            if not chunk:
                break
            
            # Update the total bytes read
            chunk_size = len(chunk)
            total_bytes_read += chunk_size
            
            # Enforce security policy: prevent resource exhaustion
            if total_bytes_read > SAFE_INPUT_LIMIT:
                raise MemoryError(f"Input size exceeds safe limit of {SAFE_INPUT_LIMIT} bytes")
            
            # Write the chunk to the output stream
            output_stream_data.write(chunk)
    
    except (OSError, IOError) as e:
        raise RuntimeError(f"Error during stream processing: {str(e)}")

    return "User input processed successfully"

# Unittests
