import sys

# Define the buffer size for reading chunks
BUFFER_SIZE = 8192

# Define a safe limit for total data processing (e.g., 100 MB)
SAFE_LIMIT = 100 * 1024 * 1024  # 100 MB

def process_stream_chunks(stream_data):
    """
    Reads and processes binary chunks from a stream.
    
    Args:
        stream_data: stream, an open stream that delivers binary data in chunks.
    
    Returns:
        str: A success message after all data chunks have been processed.
        
    Raises:
        MemoryError: If the total size of processed data surpasses SAFE_LIMIT.
        ValueError: If stream_data is not readable.
    """
    total_bytes_read = 0
    
    try:
        while True:
            chunk = stream_data.read(BUFFER_SIZE)
            if not chunk:  # End of stream
                break
            
            # Update total bytes processed
            chunk_size = len(chunk)
            total_bytes_read += chunk_size
            
            # Enforce memory safety: check against safe limit
            if total_bytes_read > SAFE_LIMIT:
                raise MemoryError("Memory limit exceeded: total processed data exceeds safe threshold.")
            
            # Simulate processing the chunk (e.g., write to output, hash, etc.)
            # In a real scenario, you'd process the chunk here (e.g., decrypt, save, validate)
            # For now, we just ensure it's read and monitored
            
    except (MemoryError, ValueError, IOError):
        # Re-raise MemoryError and other critical errors
        raise
    except Exception as e:
        # Handle unexpected stream errors
        raise IOError(f"Error reading from stream: {str(e)}")

    return "Stream processed successfully."