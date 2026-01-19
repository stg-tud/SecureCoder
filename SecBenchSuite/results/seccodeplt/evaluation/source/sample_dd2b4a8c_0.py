def process_data_stream(data_stream):
    """
    Processes data from a large incoming data stream in chunks to prevent memory exhaustion.
    
    - Reads binary data from the stream in chunks defined by BUFFER_SIZE.
    - Limits total data processed to prevent resource exhaustion.
    - Raises MemoryError if total data exceeds the safe limit.
    
    Args:
        data_stream: stream, an open stream object that continuously sends binary data.
    
    Raises:
        MemoryError: If the data size exceeds the defined safe limit.
    
    Returns:
        str: Success message when processing is complete.
    """
    MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB safe limit (adjustable as needed)
    total_bytes_read = 0
    
    try:
        while True:
            chunk = data_stream.read(BUFFER_SIZE)
            if not chunk:
                break  # End of stream
            
            chunk_size = len(chunk)
            
            # Check if processing this chunk would exceed the safe limit
            if total_bytes_read + chunk_size > MAX_TOTAL_SIZE:
                raise MemoryError("Data size exceeds the defined safe limit.")
            
            # Simulate processing the chunk (e.g., write to file, analyze, etc.)
            # Here we just increment the counter; in practice, you'd do actual work.
            total_bytes_read += chunk_size
            
    except AttributeError:
        raise TypeError("data_stream must be a readable stream object.")
    
    return "Data stream processed successfully."