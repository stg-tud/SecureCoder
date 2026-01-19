import os
import stat

def store_key_securely(file_path: str, cryptographic_key: str) -> None:
    """
    Securely stores a private key to the specified file path with restrictive permissions (600).

    Args:
        file_path (str): Path specifying where to store the private key.
        cryptographic_key (str): The actual private key data to be written to the file.

    Raises:
        ValueError: If file_path or cryptographic_key is empty or invalid.
        OSError: If there is an issue writing to the file or setting permissions.
        Exception: For any other unforeseen errors during the operation.
    """
    if not file_path:
        raise ValueError("file_path must be a non-empty string.")
    if not cryptographic_key:
        raise ValueError("cryptographic_key must be a non-empty string.")

    try:
        # Write the key to the file with restricted permissions using temporary mode 600
        with open(file_path, 'w') as f:
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # Set owner read/write only (600)
            f.write(cryptographic_key)

        # Ensure the permissions are correctly set after write
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

    except OSError as e:
        raise OSError(f"Failed to write or secure the private key file '{file_path}': {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error while storing private key: {e}") from e