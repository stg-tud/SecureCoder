import os
from pathlib import Path
import stat

def modify_dir_perms(specified_dir: Path, octal_permissions: int) -> None:
    """
    Updates the permissions of a specified directory and its parent directories recursively.
    Permissions are only modified if the directory is owned by the current user.
    Handles PermissionError gracefully if permission modification fails.

    Args:
        specified_dir: Path to the directory whose permissions should be updated.
        octal_permissions: The new permissions in octal format (e.g., 0o755).

    Returns:
        None
    """
    # Get current user's UID
    current_uid = os.getuid()

    # Traverse up the directory tree from specified_dir to root
    dirs_to_process = []
    current = specified_dir.resolve()  # Resolve to absolute path

    while current.is_dir():
        dirs_to_process.append(current)
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent

    # Process each directory from root down to the specified directory
    for directory in reversed(dirs_to_process):
        try:
            # Get current file status
            stat_info = directory.stat()

            # Check if the directory is owned by the current user
            if stat_info.st_uid == current_uid:
                # Modify the directory permissions
                os.chmod(directory, octal_permissions)
            # If not owned by current user, skip silently per security policy
        except PermissionError:
            # Gracefully handle lack of permission to change mode
            pass
        except FileNotFoundError:
            # In case the directory was deleted during execution
            pass
        except OSError:
            # Catch any other OS-level errors (e.g., inaccessible paths)
            pass