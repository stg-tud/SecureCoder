import sys
from typing import BinaryIO

# Define maximum allowed input size to prevent memory exhaustion
MAX_FORM_SIZE = 100 * 1024 * 1024  # 100 MB limit

def manage_form_submission(form_source: BinaryIO, form_destination: BinaryIO) -> str:
    """
    Handles large volumes of user-generated form data in chunks to prevent memory overload.
    
    Args:
        form_source: A readable binary stream containing the user-submitted data.
        form_destination: A writable binary stream where processed data will be written.
        
    Returns:
        A success message when the entire input has been processed.
        
    Raises:
        MemoryError: If the total input data size exceeds MAX_FORM_SIZE.
        ValueError: If the streams are not properly configured.
    """
    total_bytes_read = 0
    
    try:
        while True:
            # Read data in chunks to avoid loading everything into memory
            chunk = form_source.read(FORM_CHUNK_SIZE)
            
            if not chunk:  # End of stream
                break
                
            chunk_length = len(chunk)
            total_bytes_read += chunk_length
            
            # Enforce memory safety by checking total size
            if total_bytes_read > MAX_FORM_SIZE:
                raise MemoryError(f"Input data exceeds maximum allowed size of {MAX_FORM_SIZE} bytes")
            
            # Write the chunk to destination
            form_destination.write(chunk)
            
    except (OSError, IOError) as e:
        # Handle any I/O errors during read/write operations
        raise RuntimeError(f"Error during stream processing: {str(e)}") from e
    
    return "Form submission processed successfully"

# Unittests
