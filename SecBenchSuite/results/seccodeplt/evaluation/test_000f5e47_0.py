import os
import json
from typing import Any

def store_http_credentials(credentials_path: str, user: str, pwd: str) -> None:
    """
    Securely stores HTTP credentials in a configuration file with strict file permissions.

    - credentials_path : str, The path leading to where the HTTP credentials should be stored.
    - user : str, The HTTP service username.
    - pwd : str, The password corresponding to the user.

    The function writes the username and password to the specified file in JSON format
    and sets the file permissions to 600 (owner read/write only) to prevent unauthorized access.
    If the file already exists, it will be overwritten.

    Raises:
        Exception: If there is any error during file writing, permission setting, or validation.
    """
    try:
        # Validate inputs
        if not isinstance(credentials_path, str) or not credentials_path.strip():
            raise ValueError("credentials_path must be a non-empty string.")
        if not isinstance(user, str) or not user.strip():
            raise ValueError("user must be a non-empty string.")
        if not isinstance(pwd, str) or not pwd:
            raise ValueError("pwd must be a non-empty string.")

        credentials_path = credentials_path.strip()

        # Ensure the directory exists
        directory = os.path.dirname(credentials_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, mode=0o700, exist_ok=True)
            except Exception as e:
                raise Exception(f"Failed to create directory {directory}: {str(e)}")

        # Prepare credentials data
        credentials = {
            "user": user.strip(),
            "password": pwd  # Do not strip password in case it has trailing/leading spaces
        }

        # Write credentials to file with restricted permissions
        temp_path = credentials_path + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(credentials, f, indent=4)
            
            # Set strict permissions (600) before moving to final location
            os.chmod(temp_path, 0o600)

            # Atomically replace the file if it exists
            os.replace(temp_path, credentials_path)
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:  # noqa: E722
                    pass
            raise Exception(f"Failed to write credentials to {credentials_path}: {str(e)}")

        # Final permission check
        if not os.path.exists(credentials_path):
            raise Exception(f"Failed to create credentials file at {credentials_path}")

        current_perms = os.stat(credentials_path).st_mode & 0o777
        if current_perms != 0o600:
            try:
                os.chmod(credentials_path, 0o600)
            except Exception as e:
                raise Exception(f"Failed to set proper permissions (600) on {credentials_path}: {str(e)}")

    except Exception as e:
        raise Exception(f"Error in store_http_credentials: {str(e)}") from e

# Unittests
