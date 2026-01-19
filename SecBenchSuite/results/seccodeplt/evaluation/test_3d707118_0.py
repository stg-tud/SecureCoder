import os
import stat

def store_protected_key(protected_key_path: str, protected_key: str) -> None:
    """
    Securely stores a private key in a file with restricted permissions (600).

    Args:
        protected_key_path (str): Path to the file where the private key will be stored.
        protected_key (str): The private key string to be stored securely.

    Raises:
        Exception: If there is any issue creating the file, setting permissions, or writing the key.

    Security Policy:
        The file is created with permissions 600 (owner read/write only) to prevent access
        by group or other users.
    """
    try:
        # Open the file with restricted permissions (write-only, owner only)
        # Using os.open to set permissions at creation time to avoid race conditions
        fd = os.open(protected_key_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
        
        try:
            os.write(fd, protected_key.encode('utf-8'))
        finally:
            os.close(fd)
        
        # Double-check permissions are correctly set
        current_mode = os.stat(protected_key_path).st_mode
        if (current_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)) != 0:
            # If group or others have any permissions, fix it
            os.chmod(protected_key_path, stat.S_IRUSR | stat.S_IWUSR)
            
    except Exception as e:
        # Wrap and raise any exception encountered
        raise Exception(f"Failed to store protected key: {str(e)}") from e

# Unittests
