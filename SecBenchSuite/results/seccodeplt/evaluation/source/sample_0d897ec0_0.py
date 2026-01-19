import os
import stat

def record_private_key(key_location: str, secret_key: str) -> None:
    """
    Saves the private key content to the specified file path with secure permissions (600).

    - key_location : str, The path where the private key will be stored.
    - secret_key : str, The private key content that will be saved in the file.

    The function ensures that the file has strict permissions (read and write only for the owner),
    with no access granted to group members or others. It raises exceptions if file operations
    or permission settings fail.
    """
    try:
        # Open the file with write-only permissions, ensuring it's created securely
        with open(key_location, 'w') as key_file:
            # Write the private key content
            key_file.write(secret_key)
        
        # Set file permissions to 600 (owner: read/write, group: none, others: none)
        os.chmod(key_location, stat.S_IRUSR | stat.S_IWUSR)

    except Exception as e:
        # Clean up the file if something goes wrong after creation
        if os.path.exists(key_location):
            try:
                os.remove(key_location)
            except:
                pass  # Ignore cleanup errors
        raise e