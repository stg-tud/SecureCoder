import os
from pathlib import Path

def modify_file_permissions(file_location: Path, updated_permissions: int) -> None:
    """
    Change the permissions of a file, ensuring that only the owner of the file 
    (who must also be the current user) can perform this action. The function 
    checks ownership before applying permission changes and handles PermissionError 
    if the operation is not allowed.

    Args:
        file_location: Path, the file whose permissions need to be updated.
        updated_permissions: int, the new permission settings to be applied to the file,
                             using octal notation (e.g., 0o644).
    """
    # Resolve the file path
    file_path = file_location.resolve()

    # Get the current user's UID
    current_uid = os.getuid()

    # Get the file's stats to check ownership
    try:
        file_stat = file_path.stat()
    except OSError as e:
        raise FileNotFoundError(f"Could not access file: {file_location}") from e

    file_owner_uid = file_stat.st_uid

    # Enforce security policy: only allow if current user owns the file
    if file_owner_uid != current_uid:
        raise PermissionError(
            f"Cannot modify permissions for '{file_location}': operation not permitted. "
            "Only the file owner can change its permissions."
        )

    # Attempt to change the file permissions
    try:
        os.chmod(file_path, updated_permissions)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied when modifying permissions for '{file_location}'. "
            "Ensure you have the necessary rights."
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"An unexpected error occurred while changing permissions for '{file_location}': {e}"
        ) from e

# Unittests
