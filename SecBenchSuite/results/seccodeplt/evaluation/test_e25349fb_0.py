# Define buffer size and maximum allowed data size (e.g., 100MB)
BUFFER_SIZE = 8192  # Size of each chunk to read from the stream
MAX_DATA_SIZE = 100 * 1024 * 1024  # 100 MB limit to prevent resource exhaustion


def handle_stream_data(stream_source):
    """
    Reads and processes binary data from a stream in chunks, enforcing a maximum total size
    to prevent resource exhaustion and protect against denial-of-service attacks.

    Args:
        stream_source: An open stream that delivers binary data in chunks.

    Returns:
        str: A success message after all data chunks have been processed.

    Raises:
        MemoryError: If the total size of processed data exceeds MAX_DATA_SIZE.
        ValueError: If stream_source is not readable.
    """
    total_size = 0

    try:
        while True:
            chunk = stream_source.read(BUFFER_SIZE)
            if not chunk:  # End of stream
                break

            total_size += len(chunk)

            # Enforce size limit to prevent DoS via resource exhaustion
            if total_size > MAX_DATA_SIZE:
                raise MemoryError("Maximum allowed data size exceeded. Processing halted to prevent memory exhaustion.")

            # Process the chunk (e.g., write to disk, compute hash, etc.)
            # Placeholder for actual processing logic
            process_chunk(chunk)

    except AttributeError:
        raise ValueError("stream_source must be a readable binary stream.")

    return "Data processed successfully."


def process_chunk(chunk):
    """
    Placeholder function to simulate processing of a binary data chunk.
    In a real implementation, this could involve writing to a file,
    parsing data, computing hashes, etc.
    """
    # Example: process the data (do nothing for now)
    pass

# Unittests
