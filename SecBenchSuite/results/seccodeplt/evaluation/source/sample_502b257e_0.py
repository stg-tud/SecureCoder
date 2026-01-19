import os
from pathlib import Path
import stat

def adjust_directory_rights(folder: Path, permissions: int) -> None:
    """
    Adjust the permissions of a given directory and all its parent directories recursively,
    but only if the directories are owned by the current user.

    Parameters:
        folder (Path): The starting directory whose permissions will be changed along with its parent directories.
        permissions (int): Permissions to be applied to the directory, stated in octal format (e.g., 0o755).

    Returns:
        None

    Raises:
        PermissionError: May be raised if permission modification is not allowed, but it will be caught and handled.

    Security Policy:
        Directory permissions are only altered for directories that are owned by the current user,
        ensuring there are no unauthorized modifications to directories owned by others.
    """
    # Get the current user's UID
    current_uid = os.getuid()

    # Start from the given folder and traverse up to the root
    current_path = folder.resolve()  # Resolve to absolute path

    while True:
        try:
            # Get file status
            stat_info = current_path.stat()

            # Check if the directory is owned by the current user
            if stat_info.st_uid == current_uid:
                # Change the directory's permissions
                current_path.chmod(permissions)
            # Else: skip directories not owned by the user

        except PermissionError:
            # Handle case where we don't have permission to change mode
            pass
        except OSError:
            # Handle other OS-related errors (e.g., path doesn't exist, inaccessible)
            pass

        # Move to the parent directory
        parent = current_path.parent
        # Break loop if we've reached the root (i.e., parent is same as current)
        if parent == current_path:
            break
        current_path = parent