import sys

# Assume FORM_CHUNK_SIZE and MAX_FORM_SIZE are predefined
# Example values (these would be defined elsewhere in the system)
# FORM_CHUNK_SIZE = 64 * 1024  # 64KB chunks
# MAX_FORM_SIZE = 100 * 1024 * 1024  # 100MB max form size

def process_form_data(form_stream, storage_stream):
    """
    Processes large user-submitted form data in chunks to avoid memory exhaustion.
    
    Args:
        form_stream: A readable stream representing incoming user data.
        storage_stream: A writable stream used to store processed output data in chunks.
    
    Returns:
        str: A success message once the input is completely processed.
    
    Raises:
        MemoryError: If the total size of the input data exceeds MAX_FORM_SIZE.
    """
    total_size = 0
    
    try:
        while True:
            # Read data in chunks to avoid loading everything into memory
            chunk = form_stream.read(FORM_CHUNK_SIZE)
            
            # If no more data, we've reached the end of the stream
            if not chunk:
                break
                
            # Update total size
            total_size += len(chunk)
            
            # Enforce size limit to prevent resource overconsumption
            if total_size > MAX_FORM_SIZE:
                raise MemoryError("Form data exceeds maximum allowed size")
            
            # Write the processed chunk to storage
            storage_stream.write(chunk)
            
    except Exception as e:
        # Re-raise any unexpected exceptions
        raise e
    
    # Flush the storage stream to ensure all data is written
    storage_stream.flush()
    
    return "Form data processed successfully"