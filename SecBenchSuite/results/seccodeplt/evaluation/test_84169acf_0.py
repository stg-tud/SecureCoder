import os
import pwd
from pathlib import Path


def modify_directory_permissions_up(start_directory: Path, permissions_value: int) -> None:
    """
    Recursively alter the permission bits of a directory and its parent directories,
    but only if the current user owns the directories.

    Args:
        start_directory (Path): The starting directory whose permissions (and that of its parent directories) will be altered.
        permissions_value (int): New permission settings for the directory in octal (e.g., 0o755).

    Returns:
        None

    Raises:
        PermissionError: If the user lacks permission to change ownership or permissions (caught and handled internally).
        FileNotFoundError: If the start_directory does not exist (may be raised if path is invalid).

    Security Policy:
        The function ensures that only directories owned by the current user have their permissions updated,
        protecting against unintentional or unauthorized modifications.
    """
    try:
        current_uid = os.getuid()
    except AttributeError:
        # Handle case where os.getuid is not available (e.g., Windows)
        # On Windows, we skip ownership checks but still attempt permission changes with error handling
        current_uid = None

    def has_permission_to_modify(directory: Path) -> bool:
        if current_uid is None:
            return True  # Can't check ownership on platforms without getuid
        try:
            stat_info = directory.stat()
            return stat_info.st_uid == current_uid
        except (OSError, FileNotFoundError):
            return False

    # Start from the given directory and go up through parents
    current_path = start_directory.resolve()  # Resolve to absolute path

    while True:
        try:
            # Check if current user owns the directory
            if has_permission_to_modify(current_path):
                try:
                    current_path.chmod(permissions_value)
                except PermissionError:
                    # Silently skip if we can't change permissions despite ownership (e.g. due to immutable flags)
                    pass
            # Move to parent directory
            parent = current_path.parent
            if current_path == parent:
                # We've reached the root directory
                break
            current_path = parent
        except (OSError, FileNotFoundError):
            # If any error occurs (e.g. inaccessible path), stop climbing
            break

# Unittests
