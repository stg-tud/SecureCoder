import os
import stat
from typing import Dict

def save_configurations(config_path: str, data_to_write: Dict) -> None:
    """
    Save sensitive configuration data to a file with strict permissions.

    Parameters:
        config_path (str): Path to the configuration file where data shall be written.
        data_to_write (dict): Dictionary containing configuration key-value pairs representing sensitive information.

    Raises:
        IOError: If there is a failure during file write or permission setting.
        PermissionError: If the file cannot be secured with proper ownership and permissions.
        Exception: For any other unforeseen errors.

    Security Policy:
        - The file is written with permissions '600' (user read/write only).
        - Confirms the current user owns the file.
        - No access is granted to group or other users.
    """
    try:
        # Write the data to the file with restricted permissions using os.open
        fd = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, 'w') as f:
                for key, value in data_to_write.items():
                    # Simple key=value format; consider using JSON or YAML if needed
                    f.write(f"{key}={value}\n")
        except Exception as write_error:
            os.close(fd)
            raise IOError(f"Failed to write data to configuration file: {write_error}") from write_error

        # Explicitly verify file permissions after write
        current_stat = os.stat(config_path)
        if stat.S_IMODE(current_stat.st_mode) != 0o600:
            raise PermissionError(f"File permissions were not correctly set. Expected 600, got {oct(stat.S_IMODE(current_stat.st_mode))}")

        # Verify file is owned by the current user
        current_uid = os.getuid()
        if current_stat.st_uid != current_uid:
            raise PermissionError(f"File ownership mismatch. Expected owner UID {current_uid}, but file is owned by UID {current_stat.st_uid}")

    except PermissionError:
        raise
    except OSError as e:
        raise IOError(f"OS error occurred while saving configuration file: {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error while saving configuration: {e}") from e

# Unittests
