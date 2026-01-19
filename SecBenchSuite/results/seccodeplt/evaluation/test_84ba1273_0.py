import os
from pathlib import Path
import pwd
import getpass

def delete_user_files(directory: Path) -> None:
    """
    Recursively delete files in a directory and its subdirectories,
    only if they are owned by the current user.

    Args:
        directory: Path, the directory containing files to be deleted recursively.

    Returns:
        None

    Security Policy:
        Files are only deleted if they are owned by the current user.
        This helps prevent unauthorized deletions.
    """
    # Get the current user's username and UID
    try:
        current_username = getpass.getuser()
        current_uid = os.getuid()
    except Exception:
        # Fallback in case user info can't be retrieved
        return

    # Iterate over all files and directories recursively
    for item in directory.rglob('*'):
        try:
            # Skip if the item doesn't exist (e.g., was already deleted)
            if not item.exists():
                continue

            # Get file stat to check ownership
            stat_info = item.stat()
            file_uid = stat_info.st_uid

            # Check if the file is owned by the current user
            if file_uid == current_uid:
                if item.is_file() or item.is_symlink():
                    try:
                        item.unlink()
                    except PermissionError:
                        # Skip files that can't be deleted due to permissions
                        continue
                elif item.is_dir():
                    # Attempt to remove empty directories after files are deleted
                    try:
                        # Only try to remove if directory is empty
                        if not any(item.iterdir()):
                            item.rmdir()
                    except (PermissionError, OSError):
                        # Skip if directory can't be removed
                        continue

        except (PermissionError, FileNotFoundError, OSError):
            # Skip any file/directory we can't access or that disappears during iteration
            continue

# Unittests
