import os
import stat
from typing import Dict


def securely_store_keys(save_path: str, key_dict: Dict[str, str]) -> None:
    """
    Securely store API keys in a file with restricted permissions.

    Args:
        save_path (str): The path where the keys should be saved.
        key_dict (dict): A dictionary mapping service names to their corresponding API keys.

    Raises:
        ValueError: If save_path is empty or key_dict is empty.
        TypeError: If arguments are of incorrect type.
        OSError: If there is an issue creating, accessing, or securing the file.
        PermissionError: If the file is not owned by the current user or permissions cannot be set.

    Security Policy:
        - The file must be owned by the current user.
        - File permissions are set to 600 (read/write only by owner).
        - Ownership and permissions are validated before writing.
    """
    # Input validation
    if not isinstance(save_path, str):
        raise TypeError("save_path must be a string.")
    if not save_path:
        raise ValueError("save_path cannot be empty.")
    if not isinstance(key_dict, dict):
        raise TypeError("key_dict must be a dictionary.")
    if not key_dict:
        raise ValueError("key_dict cannot be empty.")

    # Expand user path and get absolute path
    save_path = os.path.abspath(os.path.expanduser(save_path))

    # Check if the directory exists and is writable
    dir_path = os.path.dirname(save_path)
    if not dir_path:
        dir_path = "."
    if not os.path.exists(dir_path):
        raise OSError(f"Directory does not exist: {dir_path}")
    if not os.access(dir_path, os.W_OK):
        raise PermissionError(f"Directory is not writable: {dir_path}")

    # If file already exists, verify ownership before proceeding
    uid = os.getuid()
    if os.path.exists(save_path):
        stat_info = os.stat(save_path)
        if stat_info.st_uid != uid:
            raise PermissionError(
                f"File {save_path} is not owned by the current user. Current owner UID: {stat_info.st_uid}, Expected: {uid}"
            )

        # Ensure correct permissions if file exists
        current_permissions = stat.S_IMODE(stat_info.st_mode)
        if current_permissions != 0o600:
            os.chmod(save_path, stat.S_IRUSR | stat.S_IWUSR)  # Set to 600

    # Write the keys to the file with secure permissions
    try:
        # Open file with restricted permissions (only user read/write)
        fd = os.open(save_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, 'w') as f:
            for service, api_key in key_dict.items():
                if not isinstance(service, str) or not isinstance(api_key, str):
                    raise TypeError("All keys and values in key_dict must be strings.")
                f.write(f"{service}:{api_key}\n")
    except OSError as e:
        raise OSError(f"Failed to create or write to file {save_path}: {e}")

    # Final verification of file ownership and permissions
    if not os.path.exists(save_path):
        raise OSError(f"File was not created: {save_path}")

    final_stat = os.stat(save_path)
    if final_stat.st_uid != uid:
        raise PermissionError(f"File ownership verification failed. Expected owner UID: {uid}")

    final_permissions = stat.S_IMODE(final_stat.st_mode)
    if final_permissions != 0o600:
        raise PermissionError(f"File permissions are incorrect: expected 600, got {oct(final_permissions)}")

# Unittests
