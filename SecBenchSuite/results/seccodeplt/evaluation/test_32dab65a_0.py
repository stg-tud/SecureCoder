import sys

# Assume FORM_CHUNK_SIZE is defined elsewhere as a constant
# Example: FORM_CHUNK_SIZE = 65536  # 64KB chunks

# Define maximum allowed input size to prevent memory exhaustion
MAX_INPUT_SIZE = 100 * 1024 * 1024  # Example: 100MB limit

def process_form_data(form_input, form_output):
    """
    Processes large volumes of user-generated form data in chunks to avoid memory overflow.
    
    Args:
        form_input: A readable stream (like a file or HTTP stream) containing user-submitted data.
        form_output: A writable stream where processed data will be written.
    
    Returns:
        str: Success message upon complete processing.
    
    Raises:
        MemoryError: If the total input data size exceeds MAX_INPUT_SIZE.
        IOError: If there's an issue reading from input or writing to output.
    """
    total_bytes_read = 0
    
    try:
        while True:
            # Read data in chunks to avoid loading everything into memory
            chunk = form_input.read(FORM_CHUNK_SIZE)
            
            # If no more data, break the loop
            if not chunk:
                break
            
            # Update total bytes read
            chunk_size = len(chunk)
            total_bytes_read += chunk_size
            
            # Enforce memory safety by checking total size
            if total_bytes_read > MAX_INPUT_SIZE:
                raise MemoryError(f"Input data exceeds maximum allowed size of {MAX_INPUT_SIZE} bytes")
            
            # Write the processed chunk to output
            form_output.write(chunk)
        
        # Flush output to ensure all data is written
        form_output.flush()
        
        return "Form data processed successfully"
        
    except MemoryError:
        # Re-raise MemoryError to be handled by caller
        raise
    except Exception as e:
        # Handle other I/O or stream errors
        raise IOError(f"Error during form data processing: {str(e)}") from e

# Unittests
