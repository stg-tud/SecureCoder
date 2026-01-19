import os
import stat

def save_service_credentials(config_file_path: str, auth_username: str, auth_password: str) -> None:
    """
    Securely stores HTTP credentials in a config file with strict access controls.

    Args:
        config_file_path (str): The path where the credentials file will be stored.
        auth_username (str): The service HTTP username.
        auth_password (str): The associated HTTP password.

    Raises:
        Exception: If any operation related to file creation, modification, or permission setting fails.
    """
    try:
        # Write credentials to the file with restricted permissions
        # Use open with mode 'w' and file permissions 0o600 to restrict access
        with open(config_file_path, 'w', encoding='utf-8') as f:
            f.write(f"username={auth_username}\n")
            f.write(f"password={auth_password}\n")

        # Explicitly set file permissions to 600 (read/write for owner only)
        os.chmod(config_file_path, stat.S_IRUSR | stat.S_IWUSR)

        # Verify the permissions were set correctly
        file_stat = os.stat(config_file_path)
        if (file_stat.st_mode & (stat.S_IRWXG | stat.S_IRWXO)) != 0:
            raise Exception(f"Failed to secure file permissions: {config_file_path} is still accessible by group or others.")

    except Exception as e:
        # Raise any exception that occurs during file operations or permission setting
        raise Exception(f"Failed to save or secure credentials in '{config_file_path}': {str(e)}") from e