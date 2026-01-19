import os
import stat
from pathlib import Path


def create_config_file(config_location: str, sensitive_data: dict) -> None:
    """
    Writes sensitive configuration data to a file with strict permissions.

    The file is created or overwritten at the specified location and is secured so that
    only the owner (current user) can read and write it (permissions set to 600).
    An exception is raised if writing fails or if permissions cannot be properly set.

    Args:
        config_location (str): Path to the configuration file where data shall be written.
        sensitive_data (dict): Dictionary containing sensitive key-value pairs (e.g., API keys, credentials).

    Raises:
        OSError: If there is a failure during file writing or permission setting.
        PermissionError: If the process lacks permission to create or modify the file.
        RuntimeError: If the file ownership does not match the current user after creation.
        TypeError: If sensitive_data is not a dictionary.
    """
    config_path = Path(config_location)

    # Validate input
    if not isinstance(sensitive_data, dict):
        raise TypeError("sensitive_data must be a dictionary")

    try:
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the sensitive data to the file (using mode 'w' to overwrite if exists)
        with config_path.open('w') as f:
            for key, value in sensitive_data.items():
                f.write(f"{key}={value}\n")

        # Set permissions to 600 (owner read/write only)
        config_path.chmod(0o600)

        # Verify file ownership
        current_uid = os.getuid()
        file_stat = config_path.stat()
        if file_stat.st_uid != current_uid:
            raise RuntimeError(
                f"File ownership mismatch: expected owner UID {current_uid}, but file is owned by UID {file_stat.st_uid}"
            )

        # Final check: ensure group and others have no permissions
        current_perms = file_stat.st_mode & 0o777
        if current_perms != 0o600:
            raise RuntimeError(f"File permissions were not correctly set: expected 600, got {oct(current_perms)}")

    except PermissionError as e:
        raise PermissionError(f"Permission denied when creating or modifying config file: {config_location}") from e
    except OSError as e:
        raise OSError(f"Failed to write or secure config file: {config_location}") from e

# Unittests
