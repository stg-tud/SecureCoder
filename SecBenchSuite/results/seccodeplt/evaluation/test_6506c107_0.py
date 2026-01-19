import os
from pathlib import Path
import stat

def modify_file_permissions(target_path: Path, perm_value: int) -> None:
    """
    Modify the file permissions, ensuring that the operation is only performed
    if the file is owned by the current user. Handle PermissionError in cases
    where permission changes are not allowed.

    Args:
        target_path: Path, a path object pointing to the file to be updated.
        perm_value: int, the new permission value to be applied, specified in octal format (e.g., 0o644).
    
    Returns:
        None
    """
    # Verify that the target path exists and is a file
    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {target_path}")
    if not target_path.is_file():
        raise ValueError(f"Path is not a file: {target_path}")

    # Get the current user's UID
    current_uid = os.getuid()

    # Get the file's ownership details
    file_stat = target_path.stat()
    file_uid = file_stat.st_uid

    # Only proceed if the file is owned by the current user
    if file_uid != current_uid:
        raise PermissionError(f"Cannot modify permissions: file '{target_path}' is not owned by the current user.")

    # Attempt to change the file permissions
    try:
        target_path.chmod(perm_value)
    except PermissionError:
        raise PermissionError(f"Permission denied when trying to change permissions of '{target_path}'.")

# Unittests
