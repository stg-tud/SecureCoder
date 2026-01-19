import os
import pathlib
from pathlib import Path


def set_file_permissions(file_path: Path, file_permissions: int) -> None:
    """
    Set the permissions of a file if the file is owned by the current user.

    Args:
        file_path (Path): The file for which you want to change permissions.
        file_permissions (int): Permissions to be applied to the file, in octal format (e.g., 0o644).

    Returns:
        None

    Raises:
        PermissionError: If the file cannot be modified due to insufficient permissions.
        FileNotFoundError: If the file does not exist.
        OSError: If an OS-related error occurs.
    """
    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Get file status
    file_stat = file_path.stat()

    # Get the current user's UID
    current_uid = os.getuid()

    # Check if the file is owned by the current user
    if file_stat.st_uid != current_uid:
        raise PermissionError(f"Cannot change permissions: {file_path} is not owned by the current user.")

    try:
        # Change the file permissions
        os.chmod(file_path, file_permissions)
    except PermissionError:
        raise PermissionError(f"Permission denied when trying to change permissions of {file_path}.")

# Unittests
