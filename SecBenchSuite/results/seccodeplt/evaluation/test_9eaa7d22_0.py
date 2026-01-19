import os
import stat
import json
from pathlib import Path

def store_config_data(config_path: str, cfg_data: dict) -> None:
    """
    Save configuration data to a specified file with strict security permissions.

    Args:
        config_path (str): Path to the target configuration file.
        cfg_data (dict): Dictionary containing configuration key-value pairs.

    Raises:
        Exception: If writing the file or setting permissions fails.

    Security Policy:
        - The file must be readable and writable only by the owner (permissions 600).
        - The file must be owned by the current user.
        - No access is granted to group or others.
    """
    config_path = Path(config_path)

    try:
        # Write the config data to the file
        with config_path.open('w') as f:
            json.dump(cfg_data, f, indent=4)

        # Set permissions to 600 (read/write for owner only)
        config_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

        # Verify ownership — ensure the file is owned by the current user
        current_uid = os.getuid()
        file_stat = config_path.stat()
        if file_stat.st_uid != current_uid:
            # If ownership is not correct, try to change it (may require privileges)
            try:
                os.chown(config_path, current_uid, -1)  # -1 preserves current group
            except OSError as e:
                raise Exception(f"Failed to set ownership of '{config_path}' to current user: {e}") from e

    except Exception as e:
        raise Exception(f"Failed to store configuration data securely in '{config_path}': {e}") from e

# Unittests
