import io

# Define maximum allowed input size (e.g., 100 MB)
MAX_INPUT_SIZE = 100 * 1024 * 1024  # 100 MB in bytes
FORM_CHUNK_SIZE = 8192  # 8 KB chunks for reading

def process_form_data(user_input_stream: io.IOBase, user_output_stream: io.IOBase) -> str:
    """
    Processes user-provided form data in chunks to prevent resource exhaustion.
    
    Args:
        user_input_stream: Stream object representing the user's input data
        user_output_stream: Stream object where the processed output will be written
    
    Returns:
        A message confirming successful processing of the user input.
    
    Raises:
        MemoryError: If the total processed input size exceeds MAX_INPUT_SIZE
        ValueError: If invalid stream objects are provided
    """
    if not hasattr(user_input_stream, 'read') or not hasattr(user_output_stream, 'write'):
        raise ValueError("Invalid stream objects provided")

    total_size = 0
    
    try:
        while True:
            chunk = user_input_stream.read(FORM_CHUNK_SIZE)
            
            # End of stream
            if not chunk:
                break
                
            chunk_size = len(chunk)
            total_size += chunk_size
            
            # Enforce memory limit
            if total_size > MAX_INPUT_SIZE:
                raise MemoryError(f"Input size exceeded maximum allowed limit of {MAX_INPUT_SIZE} bytes")
            
            # Write the processed chunk to output
            user_output_stream.write(chunk)
            
    except MemoryError:
        # Re-raise MemoryError if limit is exceeded
        raise
    except Exception as e:
        # Handle other potential I/O errors
        raise IOError(f"Error processing form data: {str(e)}")
    
    # Flush output to ensure all data is written
    user_output_stream.flush()
    
    return "Form data processed successfully"