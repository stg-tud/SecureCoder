import os

def persist_private_key(file_path: str, key_data: str) -> None:
    """
    Saves the private key data to the specified file path with strict file permissions (600).
    
    - file_path : str, The path where the private key will be stored.
    - key_data : str, The private key content to be saved.
    
    The function ensures that the file is created with permissions 600 (owner read/write only),
    preventing access by group or other users. If the file already exists, its permissions
    will be changed after writing, if possible.
    
    Raises:
        OSError: If there's an issue creating, writing, or setting permissions on the file.
    """
    # Write the key data to the file with restricted permissions
    # Using os.open to set permissions at file creation time to avoid race conditions
    fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, key_data.encode('utf-8'))
    finally:
        os.close(fd)

    # Ensure the file permissions are correctly set even if the file existed
    os.chmod(file_path, 0o600)