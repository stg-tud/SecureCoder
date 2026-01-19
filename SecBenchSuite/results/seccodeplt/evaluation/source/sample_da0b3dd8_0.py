import os
from pathlib import Path
import pwd
import getpass

def adjust_file_permissions(target_path: Path, new_permissions: int) -> None:
    """
    Change the permissions of a file, ensuring that only the owner of the file 
    (who must also be the current user) can perform this action.
    
    Args:
        target_path: Path, the file whose permissions need to be updated.
        new_permissions: int, the new permission settings to be applied to the file,
                         using octal notation (e.g., 0o644).
    """
    # Resolve the path to ensure it's absolute and exists
    if not target_path.exists():
        raise FileNotFoundError(f"The file {target_path} does not exist.")
    
    # Get current user's username and UID
    current_username = getpass.getuser()
    current_uid = os.getuid()
    
    # Get file status to check ownership
    try:
        file_stat = target_path.stat()
    except OSError as e:
        raise OSError(f"Could not access file metadata for {target_path}: {e}")
    
    file_uid = file_stat.st_uid
    
    # Check if the current user owns the file
    if file_uid != current_uid:
        # Try to get username for better error message
        try:
            file_owner = pwd.getpwuid(file_uid).pw_name
        except KeyError:
            file_owner = str(file_uid)
        raise PermissionError(
            f"Cannot change permissions for {target_path}: "
            f"file is owned by {file_owner}, not by current user {current_username}."
        )
    
    # Attempt to change the file permissions
    try:
        os.chmod(target_path, new_permissions)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied when changing permissions for {target_path}: {e}"
        ) from e
    except OSError as e:
        raise OSError(f"Failed to change permissions for {target_path}: {e}") from e