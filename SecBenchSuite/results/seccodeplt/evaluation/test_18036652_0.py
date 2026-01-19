import os
import stat

def save_http_auth(file_path: str, user_name: str, user_password: str) -> None:
    """
    Securely stores HTTP credentials in a config file with strict access controls.

    Args:
        file_path (str): The path where the credentials file will be stored.
        user_name (str): The service HTTP username.
        user_password (str): The associated HTTP password.

    Raises:
        Exception: If any operation related to file creation, modification, or permission setting fails.
    """
    try:
        # Write credentials to the file with restricted permissions
        # Use os.open to set permissions atomically during file creation
        fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(f"username={user_name}\n")
                f.write(f"password={user_password}\n")
        except Exception as write_error:
            os.close(fd)
            raise Exception(f"Failed to write credentials to file: {write_error}")

        # Verify that the file permissions are correctly set to 600
        current_permissions = stat.S_IMODE(os.lstat(file_path).st_mode)
        if current_permissions != 0o600:
            os.chmod(file_path, 0o600)
            # Verify again after chmod
            current_permissions = stat.S_IMODE(os.lstat(file_path).st_mode)
            if current_permissions != 0o600:
                raise Exception(f"Failed to set correct file permissions. Expected 600, got {oct(current_permissions)}")

    except OSError as e:
        raise Exception(f"File operation failed: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while saving HTTP auth: {e}")

# Unittests
