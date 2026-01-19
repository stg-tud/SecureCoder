import io

# Global constant for chunk size
CHUNK_SIZE = 8192

# Maximum allowed size for the request body (e.g., 10 MB)
MAX_REQUEST_BODY_SIZE = 10 * 1024 * 1024

def process_request(request_stream: io.IOBase) -> bytes:
    """
    Process an HTTP request body from an external stream.
    
    Reads the incoming data in small chunks to avoid loading the entire content into memory.
    Limits the total size of the request body to prevent denial-of-service attacks.
    
    Args:
        - request_stream: stream, the stream object containing the request body
    
    Returns:
        The processed request body as bytes.
    
    Raises:
        Exception: if an error occurs while processing the request or if the request
                   body exceeds the maximum allowed size.
    """
    try:
        total_size = 0
        chunks = []
        
        while True:
            chunk = request_stream.read(CHUNK_SIZE)
            
            # Check for read errors
            if isinstance(chunk, type(None)):
                raise Exception("Error reading from request stream")
            
            chunk_length = len(chunk)
            
            # Update total size
            total_size += chunk_length
            
            # Enforce maximum request body size
            if total_size > MAX_REQUEST_BODY_SIZE:
                raise Exception(f"Request body too large: exceeds {MAX_REQUEST_BODY_SIZE} bytes")
            
            # If no more data, break
            if chunk_length == 0:
                break
            
            chunks.append(chunk)
        
        # Combine all chunks into the final processed request body
        return b''.join(chunks)
    
    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")

# Unittests
