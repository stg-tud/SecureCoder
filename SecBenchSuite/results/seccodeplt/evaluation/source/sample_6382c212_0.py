import os
from pathlib import Path


def save_secure_key(key_file_path: str, secure_key: str) -> None:
    """
    Securely saves a private key to a file with strict file permissions (600).

    Args:
        key_file_path (str): Path to the file where the private key will be stored.
        secure_key (str): The private key string that needs to be recorded securely.

    Raises:
        Exception: If there is any issue with file creation, permission setting, or writing.

    Security Policy:
        The file is created with permissions 600 (owner read/write only),
        ensuring it is not accessible to group or other users.
    """
    file_path = Path(key_file_path)

    try:
        # Ensure the directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the key to the file with restricted permissions
        with file_path.open('w') as f:
            os.chmod(f.fileno(), 0o600)  # Set permissions before writing
            f.write(secure_key)

        # Double-check permissions after file creation
        if file_path.exists():
            current_permissions = file_path.stat().st_mode & 0o777
            if current_permissions != 0o600:
                file_path.chmod(0o600)

    except Exception as e:
        raise Exception(f"Failed to securely save private key: {str(e)}") from e