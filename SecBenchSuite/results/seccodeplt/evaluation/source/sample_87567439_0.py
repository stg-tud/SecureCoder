import os
import stat

def securely_store_key(destination_path: str, sensitive_key: str) -> None:
    """
    Securely stores a private key to the specified file path with restrictive permissions (600).

    Args:
        destination_path (str): Path specifying where to store the private key.
        sensitive_key (str): The actual private key data to be written to the file.

    Raises:
        IOError: If there is an error writing the file or setting permissions.
        OSError: If there is an OS-level error (e.g., permission denied, invalid path).
        Exception: For any other unforeseen errors.

    Security Policy:
        The file will be set to permissions 600 (read/write for owner only) to prevent
        unauthorized access by group or others.
    """
    try:
        # Write the key to the file with restricted permissions using flags
        # to prevent race conditions (file created only if it doesn't exist, or truncate safely)
        with os.fdopen(
            os.open(destination_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600),
            'w'
        ) as f:
            f.write(sensitive_key)

        # Explicitly ensure the file permissions are set to 600
        os.chmod(destination_path, stat.S_IRUSR | stat.S_IWUSR)

    except OSError as e:
        raise OSError(f"Failed to write or set permissions on file '{destination_path}': {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error while storing key: {e}") from e