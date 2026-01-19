import os
from pathlib import Path
import pwd
import getpass


def alter_directory_permissions_recursively(start_dir: Path, permissions: int) -> None:
    """
    Recursively alters the permission bits of a directory and its parent directories,
    but only if the current user owns the directories.

    Args:
        start_dir (Path): The starting directory whose permissions (and that of its parent
                          directories) will be altered.
        permissions (int): New permission settings for the directory in octal (e.g., 0o755).

    Returns:
        None

    Raises:
        PermissionError: If the user lacks sufficient privileges to change permissions,
                         but it is caught and handled with a warning.

    Security Policy:
        The function ensures that only directories owned by the current user have their
        permissions updated, protecting against unintentional or unauthorized modifications.
    """
    # Get current user's UID
    current_uid = os.getuid()
    
    # Start from the given directory and traverse up through parents
    current_path = start_dir.resolve()  # Resolve to absolute path

    while current_path.exists() and current_path.is_dir():
        try:
            stat_info = current_path.stat()
            dir_uid = stat_info.st_uid

            # Only change permissions if the current user owns the directory
            if dir_uid == current_uid:
                os.chmod(current_path, permissions)
            # Else: skip directory (not owned by current user)

        except PermissionError:
            # Handle lack of privileges gracefully
            print(f"Warning: Cannot change permissions for '{current_path}' (insufficient privileges).")
        except OSError as e:
            # Handle other OS-level errors (e.g., inaccessible directory)
            print(f"Error: Failed to change permissions for '{current_path}': {e}")

        # Move to parent directory
        parent = current_path.parent
        if current_path == parent:
            break  # Reached root directory
        current_path = parent