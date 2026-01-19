import os
import stat
from typing import NoReturn


def save_service_credentials(credentials_file: str, api_user: str, api_pass: str) -> None:
    """
    Securely saves HTTP credentials to a configuration file with strict access controls.

    The credentials are stored in a key=value format. The file is created with permissions
    set to 600 (owner read/write only), ensuring that only the owner can read or modify
    the file. The function raises an exception if any step fails.

    Args:
        credentials_file (str): The path where the HTTP credentials should be stored.
        api_user (str): The HTTP service username.
        api_pass (str): The password corresponding to the user.

    Raises:
        OSError: If there is an error creating, writing, or setting permissions on the file.
        ValueError: If required arguments are empty or None.
    """
    # Validate inputs
    if not credentials_file:
        raise ValueError("Credentials file path cannot be empty or None.")
    if not api_user:
        raise ValueError("API user cannot be empty or None.")
    if not api_pass:
        raise ValueError("API password cannot be empty or None.")

    # Ensure the directory exists
    credentials_dir = os.path.dirname(credentials_file)
    if credentials_dir and not os.path.exists(credentials_dir):
        try:
            os.makedirs(credentials_dir, mode=0o700, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory {credentials_dir}: {e}") from e

    # Prepare credential content
    content = f"api_user={api_user}\napi_pass={api_pass}\n"

    # Write the credentials securely
    try:
        # Use open with mode 'x' to avoid race conditions (fails if file exists)
        with open(credentials_file, 'x') as f:
            f.write(content)
    except FileExistsError:
        # If file exists, overwrite securely after truncating
        try:
            with open(credentials_file, 'w') as f:
                f.write(content)
        except OSError as e:
            raise OSError(f"Failed to write to credentials file {credentials_file}: {e}") from e
    except OSError as e:
        raise OSError(f"Failed to create credentials file {credentials_file}: {e}") from e

    # Set strict file permissions: owner read/write only (600)
    try:
        os.chmod(credentials_file, stat.S_IRUSR | stat.S_IWUSR)
    except OSError as e:
        raise OSError(f"Failed to set file permissions on {credentials_file}: {e}") from e

    # Optional: Ensure file ownership is correct (current user)
    # This is best effort; failure may occur without elevated privileges
    try:
        uid = os.getuid()
        gid = os.getgid()
        current_stat = os.stat(credentials_file)
        if current_stat.st_uid != uid or current_stat.st_gid != gid:
            os.chown(credentials_file, uid, gid)
    except (OSError, AttributeError) as e:
        # On some platforms (e.g., Windows), os.chown may not be available
        # Or the process may lack privilege. This is non-fatal but should be noted.
        pass  # Optionally log a warning in a real-world scenario

# Unittests
