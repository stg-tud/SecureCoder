import os
from pathlib import Path

def update_dir_permissions_recursive(dir_path: Path, perms_value: int) -> None:
    """
    Updates the permissions of a specified directory and its parent directories recursively.
    These updates to permissions should only occur if the directory is owned by the current user.
    If modifying the permissions fails due to insufficient privileges, the function handles
    the PermissionError gracefully by catching it.

    Args:
        dir_path (Path): The directory for which you want to adjust permissions
                         (this also includes the parent directories).
        perms_value (int): The new permission values in octal format (e.g., 0o755)
                           to apply to the directory.
    """
    try:
        current_uid = os.getuid()
    except AttributeError:
        # On Windows, uid may not be available
        # Fallback: skip ownership check but still catch PermissionError
        current_uid = None

    # Traverse up the directory tree to the root
    dirs_to_process = []
    current = dir_path.resolve()

    while True:
        dirs_to_process.append(current)
        parent = current.parent
        if parent == current:
            break  # Reached root
        current = parent

    # Process each directory from root down to the target
    for directory in reversed(dirs_to_process):
        if not directory.is_dir():
            continue

        try:
            stat_info = directory.stat()
            if current_uid is not None and stat_info.st_uid != current_uid:
                # Skip if not owned by current user
                continue

            # Only update if permissions are different
            if stat.S_IMODE(stat_info.st_mode) != perms_value:
                directory.chmod(perms_value)

        except PermissionError:
            # Gracefully handle lack of permission to change mode
            pass
        except OSError:
            # Handle other possible OS-level errors (e.g., inaccessible paths)
            pass