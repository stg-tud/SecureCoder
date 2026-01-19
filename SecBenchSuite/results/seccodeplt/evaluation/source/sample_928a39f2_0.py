import sys

# Assume FORM_CHUNK_SIZE and MAX_FORM_SIZE are predefined
# Example values (these would be set elsewhere in the system):
# FORM_CHUNK_SIZE = 8192  # 8KB chunks
# MAX_FORM_SIZE = 10485760  # 10MB maximum

def handle_user_data(data_stream, result_stream):
    """
    Processes large user-submitted data from web forms in chunks to avoid memory exhaustion.
    
    Args:
        data_stream: stream, represents the incoming user data stream
        result_stream: stream, used to store processed output data in chunks
    
    Returns:
        str: A success message once the input is completely processed.
    
    Raises:
        MemoryError: If the total size of the input data exceeds the defined permissible limit.
    """
    total_size = 0
    limit = MAX_FORM_SIZE  # Maximum allowed size for the form data

    try:
        while True:
            # Read data in chunks to prevent excessive memory usage
            chunk = data_stream.read(FORM_CHUNK_SIZE)
            
            # If no more data, we've finished reading
            if not chunk:
                break

            chunk_length = len(chunk)
            total_size += chunk_length

            # Enforce security policy: check if total size exceeds limit
            if total_size > limit:
                raise MemoryError("Maximum form data size exceeded")

            # Write the processed chunk to the result stream
            result_stream.write(chunk)
            result_stream.flush()  # Ensure data is written promptly

    except AttributeError as e:
        raise TypeError(f"Expected stream objects with read/write methods: {e}")
    
    return "Data processed successfully"