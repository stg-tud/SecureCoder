import os
import stat
from typing import Dict

def store_configuration_file(path_to_config: str, config_details: Dict) -> None:
    """
    Store sensitive configuration data to a file with secure permissions.

    Args:
        path_to_config (str): Path to the configuration file where data shall be written.
        config_details (dict): Dictionary containing configuration key-value pairs representing sensitive information.

    Raises:
        IOError: If there is a failure during the file write process.
        PermissionError: If the file cannot be secured with proper permissions or ownership.
        Exception: If ownership verification fails after writing.

    Security Policy:
        - The file will be created with permissions 600 (user read/write only).
        - No access is granted to group or other users.
        - The file must be owned by the current user.
    """
    try:
        # Write configuration data to the file securely using temporary permissions 600
        with open(path_to_config, 'w') as f:
            os.chmod(path_to_config, stat.S_IRUSR | stat.S_IWUSR)  # Set 600 before writing
            for key, value in config_details.items():
                f.write(f"{key}={value}\n")
        
        # Explicitly set permissions again after write in case default umask interfered
        os.chmod(path_to_config, stat.S_IRUSR | stat.S_IWUSR)  # 600

        # Verify file ownership
        file_stat = os.stat(path_to_config)
        current_uid = os.geteuid() if hasattr(os, 'geteuid') else os.getuid()

        if file_stat.st_uid != current_uid:
            raise PermissionError(f"File ownership mismatch: expected owner UID {current_uid}, but got {file_stat.st_uid}.")

        # Final permission check
        if file_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH):
            current_perms = stat.filemode(file_stat.st_mode)
            raise PermissionError(f"Unsafe file permissions detected: {current_perms}. Expected 600 (user read/write only).")

    except PermissionError:
        # Re-raise permission-related errors
        raise
    except OSError as e:
        raise IOError(f"Failed to write configuration file to {path_to_config}: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Unexpected error while storing configuration file: {str(e)}") from e