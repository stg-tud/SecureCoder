import os
import stat
import json
from typing import Dict


def save_secrets(secret_file: str, keys: Dict[str, str]) -> None:
    """
    Save API keys securely to a file with restricted permissions.

    The file will have read/write permissions only for the owner. Before writing,
    the function ensures that the file (if it exists) is owned by the current user.
    If the file does not exist, it will be created and owned by the current user.

    Args:
        secret_file (str): The path to the file where the API keys should be saved.
        keys (dict): A dictionary containing service names as keys and API keys as values.

    Raises:
        PermissionError: If the file is not owned by the current user or if permission
                         is denied during file operations.
        OSError: If an error occurs during file writing or permission setting.
        TypeError: If 'keys' is not a dictionary.
        ValueError: If 'keys' is empty.
    """
    if not isinstance(keys, dict):
        raise TypeError("Keys must be a dictionary.")
    if not keys:
        raise ValueError("Keys dictionary cannot be empty.")

    uid = os.getuid()

    # Check if file exists and verify ownership
    if os.path.exists(secret_file):
        file_stat = os.stat(secret_file)
        if file_stat.st_uid != uid:
            raise PermissionError(f"File {secret_file} is not owned by the current user.")
    else:
        # Ensure the directory exists
        dir_name = os.path.dirname(secret_file) or '.'
        if not os.path.exists(dir_name):
            raise FileNotFoundError(f"Directory does not exist: {dir_name}")
        if not os.access(dir_name, os.W_OK):
            raise PermissionError(f"Directory is not writable: {dir_name}")

    try:
        # Write the file with restricted permissions
        with open(secret_file, 'w') as f:
            json.dump(keys, f, indent=4)

        # Set file permissions to owner read/write only (0o600)
        os.chmod(secret_file, stat.S_IRUSR | stat.S_IWUSR)  # 0o600

        # Double-check ownership after creation/modification
        file_stat = os.stat(secret_file)
        if file_stat.st_uid != uid:
            # This should not happen when creating a file, but verify anyway
            raise PermissionError(f"File {secret_file} is not owned by the current user.")
    except PermissionError:
        raise
    except OSError as e:
        raise OSError(f"Failed to write or secure the secrets file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while saving secrets: {e}") from e

# Unittests
