import os
import json
from typing import Dict


def log_configuration(config_log: str, config_map: Dict[str, str]) -> None:
    """
    Writes sensitive configuration data to a file with strict permissions (600).
    Ensures the file is only readable and writable by the owner (current user).

    Args:
        config_log (str): Full path of the configuration file to be written.
        config_map (dict): Configuration key-value pairs.

    Raises:
        ValueError: If config_map is empty or config_log path is invalid.
        IOError: If there's an error writing to the file or setting permissions.
        OSError: If there's an OS-level error (e.g., permission denied, invalid path).
    """
    if not config_map:
        raise ValueError("config_map must not be empty")

    if not config_log:
        raise ValueError("config_log path must be provided")

    try:
        # Write configuration data to the file with restricted permissions
        # Use mode 'w' with permissions 0o600 to restrict access from the start
        fd = os.open(config_log, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(config_map, f, indent=4)

        # Double-check permissions and ownership
        stat_info = os.stat(config_log)
        current_uid = os.getuid()

        if stat_info.st_uid != current_uid:
            raise OSError(f"File ownership mismatch: expected owner {current_uid}, got {stat_info.st_uid}")

        if stat_info.st_mode & 0o777 != 0o600:
            raise OSError(f"File permissions are not 600: current permissions are {oct(stat_info.st_mode & 0o777)}")

    except (OSError, IOError) as e:
        # Catch any OS or I/O errors and re-raise as appropriate
        raise type(e)(f"Failed to write configuration or set secure permissions: {str(e)}") from e
    except Exception as e:
        # Catch any other unexpected errors
        raise IOError(f"Unexpected error while logging configuration: {str(e)}") from e