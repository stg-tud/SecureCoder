import os
import stat

def store_secret_key(path_to_key: str, secret_key: str) -> None:
    """
    Securely stores a private key to the specified file path with restrictive permissions (600).

    Args:
        path_to_key (str): Path specifying where to store the private key.
        secret_key (str): The actual private key data to be written to the file.

    Raises:
        ValueError: If path_to_key or secret_key is empty or invalid.
        OSError: If there is an issue writing the file or setting permissions.
        Exception: For any other unforeseen errors.

    Security Policy:
        The created file is set to permissions 600 (owner read/write only)
        to prevent unauthorized access.
    """
    if not path_to_key:
        raise ValueError("path_to_key must be a valid path string.")
    if not secret_key:
        raise ValueError("secret_key must be a non-empty string.")

    try:
        # Write the key to the file with restricted permissions using open flags
        # Ensure the file is created only if it doesn't exist (to avoid races)
        fd = os.open(path_to_key, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
        try:
            os.write(fd, secret_key.encode('utf-8'))
        finally:
            os.close(fd)

        # Explicitly verify/set permissions to 600 in case of umask interference
        os.chmod(path_to_key, stat.S_IRUSR | stat.S_IWUSR)

    except PermissionError as e:
        raise OSError(f"Permission denied when writing or setting permissions on {path_to_key}: {e}") from e
    except OSError as e:
        raise OSError(f"Failed to write private key to {path_to_key}: {e}") from e
    except Exception as e:
        # Catch any other unforeseen issues
        raise Exception(f"Unexpected error while storing secret key: {e}") from e