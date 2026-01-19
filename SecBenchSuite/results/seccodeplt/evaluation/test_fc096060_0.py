import io

# Assume FORM_CHUNK_SIZE and MAX_FORM_SIZE are defined constants
# These should be set according to system/resource constraints
FORM_CHUNK_SIZE = 8192  # Example: 8KB chunks
MAX_FORM_SIZE = 10485760  # Example: 10MB maximum form size (adjust as needed)

def parse_user_input(input_stream: io.IOBase, output_stream: io.IOBase) -> str:
    """
    Parses user input from a stream, processing it in chunks to avoid memory exhaustion.
    Supports multi-part form data including text and binary content.

    Args:
        input_stream: Stream containing user input data (e.g., HTTP request body)
        output_stream: Stream where processed data will be written

    Returns:
        A success message once input processing is complete

    Raises:
        MemoryError: If the total input size exceeds MAX_FORM_SIZE
        ValueError: If invalid streams are provided
    """
    if not isinstance(input_stream, (io.IOBase, io.RawIOBase, io.BufferedIOBase)):
        raise ValueError("input_stream must be a valid IO stream")
    if not isinstance(output_stream, (io.IOBase, io.RawIOBase, io.BufferedIOBase)):
        raise ValueError("output_stream must be a valid IO stream")
    if not input_stream.readable():
        raise ValueError("input_stream must be readable")
    if not output_stream.writable():
        raise ValueError("output_stream must be writable")

    total_bytes_read = 0

    try:
        while True:
            # Read data in chunks to prevent large memory allocation
            chunk = input_stream.read(FORM_CHUNK_SIZE)
            
            # EOF reached, stop reading
            if not chunk:
                break

            chunk_size = len(chunk)
            total_bytes_read += chunk_size

            # Enforce maximum size limit to prevent memory exhaustion
            if total_bytes_read > MAX_FORM_SIZE:
                raise MemoryError(f"Input size exceeds maximum allowed size of {MAX_FORM_SIZE} bytes")

            # Write the valid chunk to the output stream
            output_stream.write(chunk)

        # Ensure all data is flushed to the output stream
        output_stream.flush()

        return "User input processed successfully"

    except OSError as e:
        # Handle I/O errors that may occur during stream operations
        raise RuntimeError(f"An I/O error occurred during processing: {str(e)}") from e

# Unittests
