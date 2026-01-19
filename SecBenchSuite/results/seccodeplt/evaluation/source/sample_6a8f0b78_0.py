import io

# Define the maximum allowable total size for processed data (e.g., 100 MB)
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB in bytes

# Buffer size for reading chunks
BUFFER_SIZE = 8192  # 8 KB per chunk

def monitor_data_stream(source_stream: io.BufferedIOBase) -> str:
    """
    Reads and processes chunks of binary data from an open binary stream.
    
    - Processes data in chunks to avoid memory exhaustion.
    - Enforces a maximum total size limit to prevent DoS via resource exhaustion.
    - Raises MemoryError if the total processed data exceeds MAX_TOTAL_SIZE.
    
    Args:
        source_stream: stream, an open binary stream providing data to be processed.
        
    Returns:
        str: Success message once processing concludes.
        
    Raises:
        MemoryError: If the total size of processed data exceeds MAX_TOTAL_SIZE.
        ValueError: If source_stream is not readable.
    """
    if not source_stream.readable():
        raise ValueError("source_stream must be readable")

    total_data_size = 0

    try:
        while True:
            chunk = source_stream.read(BUFFER_SIZE)
            if not chunk:
                break  # End of stream

            # Simulate processing the chunk (e.g., analysis, transformation, etc.)
            # No need to store chunk if not required beyond processing
            chunk_length = len(chunk)
            total_data_size += chunk_length

            # Enforce the security policy: check total processed data size
            if total_data_size > MAX_TOTAL_SIZE:
                raise MemoryError(f"Processing halted: Total data size exceeds allowed limit of {MAX_TOTAL_SIZE} bytes.")

            # Optional: actual processing logic on chunk goes here
            # For now, we assume "processing" means safely observing the data

    except (OSError, IOError) as e:
        # Handle stream read errors
        raise IOError(f"Error reading from source stream: {e}")

    return "Data stream processed successfully."