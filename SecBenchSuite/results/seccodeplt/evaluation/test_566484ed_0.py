import os
import json
from typing import Dict

def secure_config_save(file_name: str, sensitive_data: Dict[str, str]) -> None:
    """
    Securely saves sensitive configuration data to a specified file with restricted permissions.

    - Writes the sensitive_data dictionary to the file in JSON format.
    - Ensures the file is only readable and writable by the owner (permissions set to 600).
    - Confirms the file is owned by the current user.
    - Raises an exception if writing fails or if permissions cannot be properly set.

    Args:
        file_name (str): Path to the target configuration file.
        sensitive_data (dict): Dictionary of sensitive configuration key-value pairs.

    Raises:
        Exception: If there is a failure in writing the file or setting file permissions/ownership.
    """
    try:
        # Write the sensitive data to the file with restricted permissions
        # Use os.open to set permissions during file creation (mitigates race conditions)
        fd = os.open(file_name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(sensitive_data, f, indent=4)
        except Exception as write_error:
            os.close(fd)  # Ensure fd is closed if json.dump fails
            raise Exception(f"Failed to write data to {file_name}: {str(write_error)}")

        # Explicitly set ownership to the current user (UID)
        current_uid = os.getuid()
        current_gid = os.getgid()
        try:
            os.chown(file_name, current_uid, current_gid)
        except Exception as chown_error:
            raise Exception(f"Failed to set ownership of {file_name} to current user: {str(chown_error)}")

        # Verify permissions are correctly set to 600
        stat_info = os.stat(file_name)
        if stat_info.st_mode & 0o777 != 0o600:
            raise Exception(f"File permissions are incorrect: expected 600, got {oct(stat_info.st_mode & 0o777)}")

        # Verify ownership
        if stat_info.st_uid != current_uid:
            raise Exception(f"File ownership incorrect: expected UID {current_uid}, got {stat_info.st_uid}")

    except Exception as e:
        # Re-raise the exception after catching
        raise Exception(f"secure_config_save failed: {str(e)}") from e

# Unittests
