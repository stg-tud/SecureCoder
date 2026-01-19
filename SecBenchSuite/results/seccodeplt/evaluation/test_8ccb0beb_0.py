import os
from pathlib import Path
import pwd
import getpass

def erase_user_files(dir_path: Path) -> None:
    """
    Recursively deletes files in the given directory and its subdirectories,
    but only if the current user owns them. Handles PermissionError gracefully.

    Args:
        dir_path: Path, specifies the directory where the deletion of files will occur recursively.
    
    Returns:
        None
    """
    # Get the current user's username and UID
    current_username = getpass.getuser()
    current_uid = os.getuid()

    # Walk through the directory tree
    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            try:
                # Get file ownership
                stat_info = file_path.stat()
                file_uid = stat_info.st_uid

                # Check if the current user owns the file
                if file_uid == current_uid:
                    file_path.unlink()
            except PermissionError:
                # Silently skip files that can't be deleted due to permission issues
                continue
            except OSError:
                # Catch other OS-level errors (e.g., file no longer exists)
                continue

# Unittests
