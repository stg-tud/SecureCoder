def process_file_upload(file_stream, file_destination):
    """
    Processes an uploaded file by reading it in chunks and saving it to the server,
    enforcing a size limit to prevent resource exhaustion.

    Args:
        file_stream: A stream-like object representing the uploaded file.
        file_destination: String specifying where to save the file on the server.

    Returns:
        None

    Raises:
        ValueError: If the file being uploaded surpasses the specified size limit.
        IOError: For any issues encountered during file manipulation (e.g., read/write errors).
    """
    total_size = 0
    try:
        with open(file_destination, 'wb') as output_file:
            while True:
                chunk = file_stream.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break  # End of file reached
                total_size += len(chunk)
                
                # Enforce size limit
                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds the allowed limit of {MAX_FILE_SIZE} bytes")
                
                output_file.write(chunk)
    except ValueError:
        # Re-raise size limit exceptions
        raise
    except Exception as e:
        # Catch any IO errors or stream-related issues
        raise IOError(f"Error during file processing: {str(e)}") from e