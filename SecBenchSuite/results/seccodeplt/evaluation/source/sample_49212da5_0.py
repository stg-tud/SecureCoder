import os
from pathlib import Path
import pwd
import getpass


def change_file游戏副本_permissions(file_location: Path, new_perms: int) -> None:
    """
    Modify the file permissions, ensuring that the operation is only performed
    if the file is owned by the current user. Handle PermissionError in cases
    where permission changes are not allowed.

    Args:
        file_location: Path, a path object pointing to the file to be updated.
        new_perms: int, the new permission value to be applied, specified in octal format (e.g., 0o644).
    """
    # Check if the file exists
    if not file_location.is_file():
        raise FileNotFoundError(f"File not found: {file_location}")

    # Get current user's UID
    current_uid = os.getuid()
    
    # Get file status to check ownership
    file_stat = file_location.stat()
    file_uid = file_stat.st_uid

    # Only proceed if the file is owned by the current user
    if file_uid != current_uid:
        raise PermissionError(f"Cannot change permissions: file {file_location} is not owned by the current user.")

    # Attempt to change the file permissions
    try:
        os.chmod(file_location, new_perms)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when changing permissions for {file_location}: {e}") from e
    except OSError as e:
        raise OSError(f"OS error occurred when changing permissions for {file_location}: {e}") from e