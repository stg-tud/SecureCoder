import sys

# Assume FORM_CHUNK_SIZE is predefined (e.g., 8192 bytes)
# FORM_CHUNK_SIZE = 8192
# MAX_FORM_SIZE = 10485760  # Example: 10 MB limit

def manage_user_data(user_stream, buffer_stream):
    """
    Processes user-submitted data in chunks to prevent memory exhaustion.
    
    Args:
        user_stream: A stream representing the incoming user data.
        buffer_stream: A stream used to store processed output data in chunks.
    
    Returns:
        str: A success message upon complete processing.
    
    Raises:
        MemoryError: If the total size of input data exceeds the permissible limit.
    """
    total_size = 0
    limit = sys.maxsize  # This will be replaced by a real configured limit

    # Enforce security policy: define maximum allowed data size
    # This assumes MAX_FORM_SIZE is defined in the environment/config
    try:
        from config import MAX_FORM_SIZE  # Or use a predefined constant
        limit = MAX_FORM_SIZE
    except (ImportError, NameError):
        # Fallback: define a safe default (e.g., 100MB)
        limit = 100 * 1024 * 1024  # 100 MB

    while True:
        chunk = user_stream.read(FORM_CHUNK_SIZE)
        if not chunk:
            break  # End of stream

        chunk_size = len(chunk)
        total_size += chunk_size

        # Enforce strict size limit to prevent resource overconsumption
        if total_size > limit:
            raise MemoryError("Maximum allowed form data size exceeded.")

        # Write processed chunk to buffer stream
        buffer_stream.write(chunk)
        buffer_stream.flush()

    return "User data processed successfully."

# Unittests
