import os
import pwd
from pathlib import Path


def clean_user_files(dir_path: Path) -> None:
    """
    Recursively delete files within a directory and its subdirectories,
    ensuring only files owned by the current user are removed.
    Gracefully handles PermissionError if deletion is denied.

    Args:
        dir_path: Path, indicates the directory from which files should be deleted recursively.
    """
    # Get the current user's UID
    current_uid = os.getuid()

    # Walk through the directory tree recursively
    for item in dir_path.rglob('*'):
        if item.is_file():
            try:
                # Get file status to check ownership
                stat_info = item.stat()
                if stat_info.st_uid == current_uid:
                    item.unlink()
            except PermissionError:
                # Gracefully handle lack of permission to delete
                continue
            except OSError:
                # Handle other potential issues (e.g., inaccessible file)
                continue