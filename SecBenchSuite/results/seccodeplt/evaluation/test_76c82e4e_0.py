# Global constant for maximum allowed file size (e.g., 10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # This value should be defined based on your requirements

# Global constant for chunk size when reading the file stream
FILE_CHUNK_SIZE = 8192  # Example: 8KB chunks


def save_uploaded_file(file_stream, destination_path):
    """
    Saves an uploaded file from a stream to the specified destination path in chunks,
    enforcing a maximum file size limit to prevent memory exhaustion.

    :param file_stream: A stream-like object containing the uploaded file.
    :param destination_path: A string representing the path on the server where the file will be saved.
    :raises ValueError: If the file exceeds the allowed size limit.
    :raises IOError: If there is an issue writing the file to the destination.
    """
    total_size = 0

    try:
        with open(destination_path, 'wb') as f:
            while True:
                chunk = file_stream.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise ValueError(f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes")

                f.write(chunk)
    except OSError as e:
        # Catch file system related errors (e.g., permission denied, disk full)
        raise IOError(f"Failed to write file to destination '{destination_path}': {str(e)}") from e

# Unittests
