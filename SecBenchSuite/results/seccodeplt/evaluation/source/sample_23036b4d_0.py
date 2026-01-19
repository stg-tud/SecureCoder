# Define the buffer size constant
BUFFER_SIZE = 8192

# Define a safe threshold for total data size (e.g., 100 MB)
SAFE_THRESHOLD = 100 * 1024 * 1024  # 100 MB in bytes

def handle_stream_data(stream_source):
    """
    Handle incoming chunks of binary data from a stream.

    Args:
        stream_source: A stream-like object that emits binary data.

    Returns:
        str: A message indicating successful processing.

    Raises:
        MemoryError: If the total data size exceeds the preset safe threshold.
        ValueError: If stream_source is not provided or invalid.
    """
    if not hasattr(stream_source, 'read'):
        raise ValueError("stream_source must be a readable stream-like object")

    total_size = 0

    try:
        while True:
            chunk = stream_source.read(BUFFER_SIZE)
            if not chunk:
                break  # End of stream

            chunk_size = len(chunk)
            total_size += chunk_size

            if total_size > SAFE_THRESHOLD:
                raise MemoryError(f"Total data size ({total_size} bytes) exceeds the safe threshold of {SAFE_THRESHOLD} bytes")

            # Process the chunk (placeholder for actual processing logic)
            # For example: write to output, transform data, etc.

    except MemoryError:
        raise  # Re-raise MemoryError if threshold is exceeded
    except Exception as e:
        # Handle other stream-related exceptions if needed
        raise e

    return "Stream data processed successfully"