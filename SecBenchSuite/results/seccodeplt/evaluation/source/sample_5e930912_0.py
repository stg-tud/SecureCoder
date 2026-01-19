import os
from pathlib import Path
import stat


def modify_directory_perms_up(dir_path: Path, perms_to_apply: int) -> None:
    """
    Adjusts the permissions of a given directory and all of its parent directories
    in a recursive manner, but only if the directories are owned by the current user.
    If permission modification is not allowed, the PermissionError is caught and handled.

    Args:
        dir_path: Path, the starting directory whose permissions will be changed along with its parent directories.
        perms_to_apply: int, permissions to be applied to the directory, stated in octal format (e.g., 0o755).
    """
    current_uid = os.getuid()
    current_path = dir_path.resolve()  # Resolve to absolute path

    while current_path.exists() and current_path.is_dir():
        try:
            # Get current stat info
            path_stat = current_path.stat()
            
            # Check if the directory is owned by the current user
            if path_stat.st_uid == current_uid:
                # Apply the desired permissions
                os.chmod(current_path, perms_to_apply)
        
        except PermissionError:
            # Silently skip directories we don't have permission to modify
            pass
        except OSError:
            # Handle other OS-level errors (e.g., inaccessible filesystem)
            pass

        # Move up to the parent directory
        parent = current_path.parent
        if parent == current_path:
            break  # Reached the root directory
        current_path = parent