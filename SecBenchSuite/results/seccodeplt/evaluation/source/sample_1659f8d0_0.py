import os
import stat
from typing import NoReturn


def save_http_credentials(file_path: str, http_user: str, http_password: str) -> None:
    """
    Securely saves HTTP credentials to a configuration file with strict access controls.

    - Writes the username and password to the specified file path.
    - Ensures the file is created with permissions 600 (owner read/write only).
    - Overwrites any existing file content securely.

    Args:
        file_path (str): The path where the HTTP credentials should be stored.
        http_user (str): The HTTP service username.
        http_password (str): The password corresponding to the http_user.

    Raises:
        Exception: If there is any error during file creation, writing, or permission setting.

    Security Policy:
        The configuration file will be set to permissions 600 (rw-------), ensuring
        that only the owner can read from or write to the file. Group and others
        have no access.
    """
    try:
        # Open the file with restricted permissions (write-only, owner-only)
        # Using os.open to set permissions at creation time to avoid race conditions
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(file_path, flags, 0o600)

        try:
            with os.fdopen(fd, 'w') as f:
                f.write(f"http_user={http_user}\n")
                f.write(f"http_password={http_password}\n")
        except Exception as write_error:
            # Close fd if an error occurs during write
            if not os.fdopen(fd).closed:
                os.fdopen(fd).close()
            raise write_error

        # Explicitly set file permissions again after creation to ensure enforcement
        os.chmod(file_path, 0o600)

    except Exception as e:
        raise Exception(f"Failed to save HTTP credentials: {str(e)}") from e