import os
from pathlib import Path
import pwd
import getpass

def update_file_permissions(path_to_file: Path, permissions_val: int) -> None:
    """
    Modify the file permissions, ensuring that the operation is only performed
    if the file is owned by the current user. Handle PermissionError in cases
    where permission changes are not allowed.

    Args:
        path_to_file: Path object pointing to the file to be updated.
        permissions_val: New permission value in octal format (e.g., 0o644).

    Returns:
        None

    Security Policy:
        The modification of permissions is restricted to files owned by the
        user executing the operation to avoid unintentional or malicious changes.
    """
    # Resolve the path to handle symbolic links if needed
    if not path_to_file.exists():
        raise FileNotFoundError(f"The file {path_to_file} does not exist.")

    # Get current user's UID
    current_username = getpass.getuser()
    current_uid = os.getuid()

    # Get file stat info
    try:
        file_stat = path_to_file.stat()
    except OSError as e:
        raise OSError(f"Could not access file metadata: {e}")

    # Check if the file is owned by the current user
    if file_stat.st_uid != current_uid:
        # Optional: resolve UID to username for a clearer message
        try:
            file_owner = pwd.getpwuid(file_stat.st_uid).pw_name
        except KeyError:
            file_owner = str(file_stat.st_uid)
        raise PermissionError(
            f"Cannot change permissions: file is owned by '{file_owner}', "
            f"not by current user '{current_username}'."
        )

    # Attempt to change the file permissions
    try:
        path_to_file.chmod(permissions_val)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when changing permissions: {e}")
    except OSError as e:
        raise OSError(f"Unexpected error when changing file permissions: {e}")