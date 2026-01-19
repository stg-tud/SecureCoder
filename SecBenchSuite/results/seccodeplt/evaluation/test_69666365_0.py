import os
from pathlib import Path
import pwd
import getpass


def adjust_directory_perms_recursively(target_dir: Path, new_perms: int) -> None:
    """
    Updates the permissions of a specified directory and its parent directories recursively.
    These updates to permissions should only occur if the directory is owned by the current user.
    If modifying the permissions fails due to insufficient privileges, the function should handle
    the PermissionError gracefully by catching it.

    :param target_dir: Path, the directory for which you want to adjust permissions (this also includes the parent directories).
    :param new_perms: int, the new permission values in octal format (e.g., 0o755) to apply to the directory.
    """
    current_username = getpass.getuser()

    # Resolve the target directory to absolute path
    target_dir = target_dir.resolve()

    # Traverse up the directory tree to the root
    dirs_to_process = []
    current = target_dir
    while True:
        dirs_to_process.append(current)
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent

    # Process each directory from root down to the target (to ensure parent dirs are handled first if needed)
    for directory in reversed(dirs_to_process):
        if not directory.is_dir():
            continue

        try:
            # Get the directory's stat info
            stat_info = directory.stat()
            dir_uid = stat_info.st_uid

            # Lookup username from UID
            try:
                dir_owner = pwd.getpwuid(dir_uid).pw_name
            except KeyError:
                # UID exists but no passwd entry (e.g., system users), skip
                continue

            # Check if the directory is owned by the current user
            if dir_owner == current_username:
                # Apply new permissions
                os.chmod(directory, new_perms)
        except PermissionError:
            # Silently skip if we lack permission to change the mode
            pass
        except OSError:
            # Handle other OS-level errors (e.g., inaccessible directory)
            pass

# Unittests
