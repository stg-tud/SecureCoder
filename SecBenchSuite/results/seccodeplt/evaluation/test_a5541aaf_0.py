import os
import stat
from pathlib import Path


def set_http_credentials(config_path: str, username: str, password: str) -> None:
    """
    Store HTTP credentials securely in a configuration file.

    Args:
        config_path (str): The file path where HTTP credentials will be stored.
        username (str): The HTTP username for the service.
        password (str): The associated password.

    Raises:
        Exception: If any error occurs during validation, file creation, or permission setting.

    Security:
        - Ensures the file has permissions 600 (owner read/write only).
        - Validates that the file is owned by the current user.
        - Prevents access by group or others.
    """
    config_path = Path(config_path)

    try:
        # Validate inputs
        if not username:
            raise ValueError("Username cannot be empty or None")
        if not password:
            raise ValueError("Password cannot be empty or None")

        # Ensure parent directory exists
        if config_path.exists() and config_path.is_dir():
            raise FileExistsError(f"Config path '{config_path}' is a directory, not a file.")
        
        parent_dir = config_path.parent
        if not parent_dir.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

        if not parent_dir.is_dir():
            raise NotADirectoryError(f"Parent path is not a directory: {parent_dir}")

        # Write credentials to file with restricted permissions
        temp_path = str(config_path) + ".tmp"
        try:
            # Write to a temporary file first
            with open(temp_path, 'w') as f:
                f.write(f"username={username}\n")
                f.write(f"password={password}\n")

            # Set strict permissions before moving to final location
            os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)  # 600 permissions

            # Atomically replace the file if it exists
            os.replace(temp_path, config_path)

        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:  # noqa: E722
                    pass
            raise e

        # Final security validation
        file_stat = config_path.stat()

        # Check permissions: must be 600 (0o600)
        if file_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
            # If permissions are too permissive, fix them
            os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)
            # Re-check
            file_stat = config_path.stat()
            if file_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
                raise PermissionError(
                    f"Unable to set secure permissions on {config_path}. "
                    "File must not be readable or writable by group or others."
                )

        # Check ownership (only validate if running under a multi-user OS like Unix)
        if hasattr(os, 'getuid'):
            current_uid = os.getuid()
            if file_stat.st_uid != current_uid:
                try:
                    # Attempt to change ownership back to current user
                    os.chown(config_path, current_uid, -1)
                except PermissionError:
                    raise PermissionError(
                        f"File {config_path} is owned by UID {file_stat.st_uid}, "
                        f"but must be owned by current user ({current_uid})."
                    )

        # Final confirmation of secure state
        if (file_stat.st_mode & 0o777) != 0o600:
            raise RuntimeError(f"Failed to secure file {config_path}: expected 600, got {file_stat.st_mode & 0o777:o}")

    except (Exception) as e:
        raise RuntimeError(f"Failed to set HTTP credentials: {str(e)}") from e

# Unittests
