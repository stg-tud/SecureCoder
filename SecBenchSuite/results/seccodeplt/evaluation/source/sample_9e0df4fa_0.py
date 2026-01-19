import sys

# Define buffer size for reading chunks
BUFFER_SIZE = 8192  # 8 KB per chunk

# Define maximum allowable total data size to prevent memory exhaustion
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB limit

def handle_data_stream(input_stream):
    """
    Process a large binary data stream in chunks to prevent memory exhaustion.

    Args:
        - input_stream: stream, an open binary stream providing data to be processed.

    Returns:
        str: Success message once processing concludes.

    Raises:
        MemoryError: If the size of processed data exceeds the established safety limit.
        ValueError: If input_stream is not readable or not a valid stream.

    Security Policy:
        The function enforces a MAX_TOTAL_SIZE limit to prevent denial-of-service
        via resource exhaustion from overly large or infinite streams.
    """
    if not hasattr(input_stream, 'read') or not input_stream.readable():
        raise ValueError("input_stream must be a readable binary stream")

    total_processed = 0

    try:
        while True:
            chunk = input_stream.read(BUFFER_SIZE)
            if not chunk:
                break  # End of stream

            total_processed += len(chunk)

            # Enforce security policy: prevent excessive memory usage
            if total_processed > MAX_TOTAL_SIZE:
                raise MemoryError(f"Data stream exceeds maximum allowed size of {MAX_TOTAL_SIZE} bytes")

            # Process the chunk (simulated here; in real use, perform actual processing)
            # Example: write to disk, hash, transform, etc.
            # process_chunk(chunk)  # placeholder for actual processing logic

    except (OSError, IOError) as e:
        # Handle stream read errors
        raise IOError(f"Error reading from input stream: {e}") from e

    return "Data stream processed successfully"