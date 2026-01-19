import os
import stat

def store_service_credentials(cred_file_path: str, service_username: str, service_password: str) -> None:
    """
    Securely stores HTTP credentials in a config file with strict access controls.

    Args:
        cred_file_path (str): The path where the credentials file will be stored.
        service_username (str): The service HTTP username.
        service_password (str): The associated HTTP password.

    Returns:
        None

    Raises:
        Exception: If file creation, writing, or permission setting fails.
    """
    try:
        # Write credentials to the file securely
        with open(cred_file_path, 'w') as f:
            f.write(f"username={service_username}\n")
            f.write(f"password={service_password}\n")
        
        # Set strict file permissions to 600 (owner read/write only)
        os.chmod(cred_file_path, stat.S_IRUSR | stat.S_IWUSR)

        # Verify that permissions were correctly set
        file_stat = os.stat(cred_file_path)
        current_permissions = file_stat.st_mode & 0o777
        if current_permissions != 0o600:
            raise Exception(f"Failed to set correct permissions on {cred_file_path}. "
                            f"Expected 600, got {oct(current_permissions)}")

    except Exception as e:
        # Raise any exception encountered during file operations
        raise Exception(f"Failed to securely store service credentials: {str(e)}") from e