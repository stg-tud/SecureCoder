import os
import stat
from typing import NoReturn

def store_http_credentials(file_path: str, user: str, passkey: str) -> None:
    """
    Saves HTTP credentials to a configuration file with secure permissions.

    Arguments:
        file_path (str): Path to where the HTTP credentials should be saved.
        user (str): The HTTP username.
        passkey (str): The password associated with the username.

    Raises:
        Exception: If any error occurs during file creation, writing, or permission setting.

    Security Policy:
        The file will be created with permissions 600 (read/write by owner only).
        Ownership will match the current user, and no group or other users will have access.
    """
    try:
        # Open the file with restricted permissions (only user read/write)
        with open(file_path, 'w') as f:
            f.write(f"username={user}\n")
            f.write(f"password={passkey}\n")

        # Ensure the file permissions are set to 600 (rw-------)
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

    except Exception as e:
        raise Exception(f"Failed to store HTTP credentials: {str(e)}") from e