import os
from pathlib import Path
import pwd
import getpass

def update_permissions_for_dirs(path_dir: Path, new_perms: int) -> None:
    """
    Recursively alter the permission bits of a directory and its parent directories,
    but only if the current user owns the directories.

    Args:
        path_dir (Path): The starting directory whose permissions (and that of its parent directories)
                         will be altered.
        new_perms (int): New permission settings for the directory in octal (e.g., 0o755).

    Returns:
        None

    Security Policy:
        The function ensures that only directories owned by the current user have their
        permissions updated, protecting against unintentional or unauthorized modifications.
    """
    current_user = getpass.getuser()

    def is_owned_by_user(directory: Path) -> bool:
        """Check if the given directory is owned by the current user."""
        try:
            stat_info = directory.stat()
            try:
                # Get username from uid
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
            except KeyError:
                # In case the user ID has no entry in passwd (e.g., deleted user)
                return False
            return owner == current_user
        except OSError:
            # If we can't access file stats, assume not owned or inaccessible
            return False

    # Start from path_dir and walk up through parents
    dirs_to_process = []
    current = path_dir.resolve()  # Resolve to absolute path

    while current.exists() and current.is_dir():
        dirs_to_process.append(current)
        parent = current.parent
        if parent == current:
            break  # Reached root
        current = parent

    # Apply permissions from root down to the target directory
    for directory in reversed(dirs_to_process):
        try:
            if is_owned_by_user(directory):
                os.chmod(directory, new_perms)
            # If not owned, skip silently per security policy
        except PermissionError:
            # Silently skip if we can't change permissions due to privilege issues
            pass
        except OSError:
            # Handle other OS-level errors (e.g., inaccessible directories)
            pass

# Unittests
