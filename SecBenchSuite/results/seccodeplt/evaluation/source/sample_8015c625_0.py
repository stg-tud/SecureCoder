def process_stream_chunks(binary_stream):
    """
    Process incoming chunks of binary data from a large stream with memory safety.
    
    Args:
        - binary_stream: stream, a stream-like object that emits binary data.
    
    Returns:
        Returns a message indicating successful processing once complete.
    
    Raises:
        - MemoryError: if the total data size exceeds the preset safe threshold.
    
    Security Policy:
        The function enforces a boundary on the cumulative amount of data processed
        to prevent unmanageable memory consumption and possible denial-of-service scenarios.
    """
    SAFE_THRESHOLD = 100 * 1024 * 1024  # 100 MB safe threshold
    total_processed = 0
    BUFFER_SIZE = 8192  # Size of each data chunk to be processed

    try:
        while True:
            chunk = binary_stream.read(BUFFER_SIZE)
            if not chunk:
                break  # End of stream
            
            if not isinstance(chunk, bytes):
                raise ValueError("Stream must emit binary data (bytes)")

            chunk_size = len(chunk)
            if total_processed + chunk_size > SAFE_THRESHOLD:
                raise MemoryError("Total data size exceeds the safe threshold")
            
            # Process the chunk (simulated processing)
            total_processed += chunk_size
            
    except AttributeError as e:
        if "read" in str(e):
            raise ValueError("binary_stream must be a stream-like object with a read method")
        else:
            raise

    return "Stream processed successfully"