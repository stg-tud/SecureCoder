import os

def store_private_key(location: str, key_content: str) -> None:
    """
    Saves a private key to the specified location with secure file permissions (600).

    - location: str, The path where the private key will be stored.
    - key_content: str, The private key content that will be saved in the corresponding file.

    The function ensures that the file is created with permissions 600 (owner read/write only).
    Raises exceptions if there are issues with file access, writing, or permission setting.
    """
    # Write the key content to the file with restricted permissions using os.open
    fd = os.open(location, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, key_content.encode('utf-8'))
    finally:
        os.close(fd)

    # Double-check permissions in case the umask affects the created file
    os.chmod(location, 0o600)

# Unittests
