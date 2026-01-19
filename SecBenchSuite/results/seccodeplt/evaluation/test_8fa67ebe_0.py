import os
import stat
import json
from pathlib import Path

def write_configuration(config_file: str, config_data: dict) -> None:
    """
    Writes application configuration data to a configuration file with secure permissions.

    - config_file : str, The file path where the configuration will be stored.
    - config_data : dict, A dictionary containing configuration data in the format {'key': 'value'}.

    Raises:
        Exception: If there's any issue with writing the file, setting permissions, or verifying ownership.

    Security Policy:
        - The file must have permissions 600 (owner read/write only).
        - No access is allowed for group or others.
        - The file must be owned by the current user.
    """
    config_path = Path(config_file)

    try:
        # Write the configuration data atomically to avoid partial writes
        temp_file = config_path.with_suffix(config_path.suffix + '.tmp')
        with temp_file.open('w') as f:
            json.dump(config_data, f, indent=4)

        # Replace the target file with the temp file
        temp_file.replace(config_path)

        # Set secure permissions: owner read/write only (600)
        config_path.chmod(0o600)

        # Verify file ownership
        current_uid = os.getuid()
        file_stat = config_path.stat()
        if file_stat.st_uid != current_uid:
            # Try to change ownership only if script has appropriate privileges
            try:
                os.chown(config_path, current_uid, -1)  # Change owner, keep group unchanged
            except PermissionError:
                raise Exception(f"Configuration file {config_file} is not owned by the current user "
                                f"and could not change ownership. Current owner UID: {file_stat.st_uid}")

        # Final permission check
        current_permissions = file_stat.st_mode & stat.S_IMODE(file_stat.st_mode)
        if current_permissions != 0o600:
            raise Exception(f"Failed to set correct permissions on {config_file}. "
                            f"Expected 0o600, got {oct(current_permissions)}")

        # Double-check that group and others have no access
        if current_permissions & 0o077:
            raise Exception(f"Configuration file {config_file} allows access to group or others. "
                            f"Permissions are too permissive: {oct(current_permissions)}")

    except Exception as e:
        # Catch and re-raise with context, in case of any I/O or permission issue
        raise Exception(f"Failed to write configuration file '{config_file}': {str(e)}") from e

# Unittests
