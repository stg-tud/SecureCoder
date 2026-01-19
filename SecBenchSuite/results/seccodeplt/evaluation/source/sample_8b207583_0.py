import os
from pathlib import Path
from typing import Optional

def modify_file_permissions(target_file: Path, mode: int) -> None:
    """
    Adjust the permissions of a given file, but only if the file is owned by the current user.
    
    Parameters:
        target_file (Path): The path to the target file whose permissions are to be altered.
        mode (int): The permission mode to be set for the file, represented in octal (e.g., 0o644).
    
    Returns:
        None
    
    Raises:
        PermissionError: If the file is not owned by the current user or permission is denied.
        FileNotFoundError: If the file does not exist.
        OSError: For other system-related errors.
    """
    # Ensure the file exists
    if not target_file.exists():
        raise FileNotFoundError(f"The file '{target_file}' does not exist.")
    
    if not target_file.is_file():
        raise OSError(f"'{target_file}' is not a regular file.")
    
    # Get current user's UID
    current_uid = os.getuid()
    
    # Get file ownership
    file_stat = target_file.stat()
    file_uid = file_stat.st_uid
    
    # Check if the current user owns the file
    if file_uid != current_uid:
        raise PermissionError(f"Cannot modify permissions: '{target_file}' is not owned by the current user.")
    
    # Attempt to change the file permissions
    try:
        os.chmod(target_file, mode)
    except PermissionError:
        raise PermissionError(f"Permission denied when trying to change permissions of '{target_file}'.")
    except OSError as e:
        raise OSError(f"Failed to modify permissions for '{target_file}': {e}")