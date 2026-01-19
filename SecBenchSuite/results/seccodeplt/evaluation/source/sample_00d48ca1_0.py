BUFFER_SIZE = 8192  # Size of each chunk to read from the stream
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # Maximum allowed total data size (e.g., 100 MB)

def manage_data_chunks(chunk_stream):
    """
    Reads and processes binary chunks from a stream, enforcing a maximum total data size
    to prevent resource exhaustion and potential denial-of-service attacks.

    Args:
        chunk_stream: stream, an open stream that delivers binary data in chunks.

    Returns:
        str: A success message after all data chunks have been processed.

    Raises:
        MemoryError: If the total size of processed data exceeds MAX_TOTAL_SIZE.
    """
    total_size = 0

    try:
        while True:
            chunk = chunk_stream.read(BUFFER_SIZE)
            if not chunk:  # End of stream
                break

            # Update total size
            chunk_size = len(chunk)
            total_size += chunk_size

            # Enforce memory limit
            if total_size > MAX_TOTAL_SIZE:
                raise MemoryError("Maximum allowed data size exceeded. Aborting to prevent memory exhaustion.")

            # Process the chunk (placeholder for actual processing logic)
            # Example: write to disk, hash, decrypt, etc.
            # process_chunk(chunk)

    except AttributeError:
        raise TypeError("chunk_stream must be a readable binary stream with a 'read' method.")

    return "All data chunks processed successfully."