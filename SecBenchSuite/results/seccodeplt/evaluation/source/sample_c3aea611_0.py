# Constants
BUFFER_SIZE = 8192  # Size of each chunk to read from the stream
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # Maximum total data allowed: 100 MB

def stream_data_handler(incoming_stream):
    """
    Handles large incoming binary data streams by processing data in chunks.
    
    - incoming_stream: stream, an open binary stream providing data to be processed.
    
    The function reads chunks of binary data sequentially from the stream and processes it.
    To prevent memory exhaustion with large or infinite streams, a maximum total size
    limit is enforced. If this limit is exceeded, a MemoryError is raised.
    
    Returns:
        str: A success message once processing concludes.
        
    Raises:
        MemoryError: If the size of processed data exceeds the established safety limit.
        ValueError: If the incoming_stream is not readable.
    """
    total_processed = 0

    # Validate the stream
    if not hasattr(incoming_stream, 'readable') or not incoming_stream.readable():
        raise ValueError("incoming_stream must be a readable binary stream")

    try:
        while True:
            chunk = incoming_stream.read(BUFFER_SIZE)
            if not chunk:  # End of stream
                break

            # Simulate processing the chunk (e.g., write to output, hash, parse, etc.)
            # For memory safety, we do NOT store the chunk beyond this point
            chunk_size = len(chunk)
            total_processed += chunk_size

            # Enforce security policy: prevent excessive memory usage
            if total_processed > MAX_TOTAL_SIZE:
                raise MemoryError(f"Processing aborted: Total data exceeds safety limit of {MAX_TOTAL_SIZE} bytes")

            # Optional: actual processing logic would go here
            # Example: write to disk, compute digest, transform, etc.

    except Exception as e:
        # Re-raise any unexpected exceptions (caller handles them)
        raise e

    return "Data processed successfully"