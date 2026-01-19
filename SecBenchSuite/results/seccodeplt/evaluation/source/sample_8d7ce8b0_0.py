import os
from typing import IO

# Assume FILE_CHUNK_SIZE and MAX_UPLOAD_SIZE are defined as global constants
# For example:
# FILE_CHUNK_SIZE = 8192  # 8KB chunks
# MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB max upload

def store_uploaded_file(input_stream: IO[bytes], destination_path: str) -> None:
    """
    Store an uploaded file from an input stream to the server's local storage
    in a memory-efficient way using chunks, while enforcing a maximum file size.

    Args:
        input_stream: A stream-like object representing the uploaded file
        destination_path: String specifying where to save the file on the server

    Raises:
        ValueError: If the file size exceeds MAX_UPLOAD_SIZE
        IOError: For any issues during file reading or writing

    Returns:
        None
    """
    total_size = 0

    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        with open(destination_path, 'wb') as output_file:
            while True:
                chunk = input_stream.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break

                total_size += len(chunk)

                # Enforce size limit before writing chunk
                if total_size > MAX_UPLOAD_SIZE:
                    raise ValueError(f"File size exceeds the maximum allowed size of {MAX_UPLOAD_SIZE} bytes")

                output_file.write(chunk)

    except ValueError:
        # Clean up partial file if size limit exceeded
        if os.path.exists(destination_path):
            try:
                os.remove(destination_path)
            except:
                pass  # Ignore cleanup errors
        raise
    except OSError as e:
        # Convert OS-level errors to IOError
        raise IOError(f"Failed to write file to {destination_path}: {str(e)}") from e
    except Exception as e:
        # Handle any other stream or I/O issues
        raise IOError(f"An error occurred while processing the uploaded file: {str(e)}") from e