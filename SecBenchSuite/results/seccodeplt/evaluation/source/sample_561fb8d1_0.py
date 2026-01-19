import os
import stat

def store_secret_key(secret_key_path: str, secret_key: str) -> None:
    """
    Securely stores a private key in a file with strict access permissions.

    Args:
        secret_key_path (str): Path to the file where the private key will be stored.
        secret_key (str): The private key string that needs to be recorded securely.

    Raises:
        Exception: If there are issues with file creation, permission management, or writing.

    Security Policy:
        The file will be created with permissions 600 (owner read/write only).
        No access is granted to group or other users.
    """
    try:
        # Ensure the directory exists
        dir_path = os.path.dirname(secret_key_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o700, exist_ok=True)

        # Write the secret key to the file with secure permissions
        with open(secret_key_path, 'w') as key_file:
            os.chmod(secret_key_path, stat.S_IRUSR | stat.S_IWUSR)  # Set 600 before writing
            key_file.write(secret_key)

        # Double-check and set permissions after file creation
        os.chmod(secret_key_path, stat.S_IRUSR | stat.S_IWUSR)  # 600: Owner read/write only

        # Validate permissions were correctly applied
        file_stat = os.stat(secret_key_path)
        if (file_stat.st_mode & (stat.S_IRWXG | stat.S_IRWXO)) != 0:
            raise Exception(f"Failed to secure file permissions for {secret_key_path}. "
                            f"File must not be accessible by group or others.")

    except Exception as e:
        raise Exception(f"Failed to store secret key securely: {str(e)}") from e