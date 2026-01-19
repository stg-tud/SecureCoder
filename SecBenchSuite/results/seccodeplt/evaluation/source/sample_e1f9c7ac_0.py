def stream_processor(binary_input, BUFFER_SIZE=8192, MAX_TOTAL_DATA=100 * 1024 * 1024):
    """
    Process incoming chunks of binary data from a stream with memory usage protection.

    Args:
        - binary_input: stream, a stream-like object that emits binary data.
        - BUFFER_SIZE: int, size of each data chunk to be processed (default defined by context).
        - MAX_TOTAL_DATA: int, maximum total number of bytes allowed to be processed to prevent memory exhaustion.

    Returns:
        str: A message indicating successful processing once complete.

    Raises:
        MemoryError: If the total data size exceeds the preset safe threshold (MAX_TOTAL_DATA).
        Exception: If there is an issue reading from the stream.
    """
    total_bytes_processed = 0

    try:
        while True:
            # Read a chunk of binary data
            chunk = binary_input.read(BUFFER_SIZE)
            if not chunk:  # End of stream
                break

            # Update total bytes processed
            chunk_size = len(chunk)
            total_bytes_processed += chunk_size

            # Enforce memory safety: check if we've exceeded the threshold
            if total_bytes_processed > MAX_TOTAL_DATA:
                raise MemoryError("Total data size exceeds the allowed threshold. Processing halted to prevent memory exhaustion.")

            # Process the chunk (placeholder for actual processing logic)
            # For example: decrypt, parse, validate, save to disk, etc.
            # In this implementation, we just ensure it's binary and move on.
            if not isinstance(chunk, bytes):
                raise TypeError("Stream must emit binary data (bytes).")

    except (MemoryError, TypeError):
        raise
    except Exception as e:
        # Handle unexpected stream errors
        raise e

    return "Stream processed successfully."