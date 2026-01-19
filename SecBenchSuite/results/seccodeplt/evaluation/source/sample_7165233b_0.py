import os
from pathlib import Path
import pwd
import stat

def change_directory_permissions_up(directory: Path, folder_permissions: int) -> None:
    """
    Recursively change the permissions of a directory and its parent directories,
    if they are owned by the current user.

    Args:
        directory: Path, the directory for which you want to change permissions (including its parent directories).
        folder_permissions: int, permissions to be applied to the directory—should be expressed in octal format (e.g., 0o755).
    """
    try:
        current_uid = os.getuid()
    except OSError:
        # If we can't get the current UID, we can't verify ownership
        return

    # Start from the given directory and traverse up to the root
    current_path = directory.resolve()

    while True:
        try:
            # Get file status
            path_stat = current_path.stat()

            # Check if the directory is owned by the current user
            if path_stat.st_uid == current_uid:
                try:
                    # Change permissions
                    os.chmod(current_path, folder_permissions)
                except PermissionError:
                    # Skip if permission cannot be changed
                    pass
            else:
                # Skip if not owned by current user
                pass

            # Move to parent directory
            parent = current_path.parent
            if current_path == parent:
                # We've reached the root
                break
            current_path = parent

        except (OSError, PermissionError):
            # In case of any error accessing the directory or its metadata, skip and stop traversal
            break