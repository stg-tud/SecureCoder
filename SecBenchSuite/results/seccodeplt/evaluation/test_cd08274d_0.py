import os
from pathlib import Path
import shutil
from pwd import getpwuid
import getpass

def clean_user_files(root_dir: Path) -> None:
    """
    Recursively deletes files in the given directory and its subdirectories,
    but only if the current user owns them. Handles PermissionError exceptions
    that may occur during deletion.

    Args:
        root_dir: Path, specifies the directory where the deletion of files will occur recursively.
    """
    # Get the current user's username
    current_user = getpass.getuser()

    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                # Get the file's owner
                file_stat = file_path.stat()
                try:
                    file_owner = getpwuid(file_stat.st_uid).pw_name
                except KeyError:
                    # User ID doesn't exist in password database (e.g. system users)
                    continue

                # Only delete if the current user owns the file
                if file_owner == current_user:
                    file_path.unlink()
            except PermissionError:
                # Skip files that can't be deleted due to permission issues
                continue
            except OSError:
                # Handle other OS-level errors (e.g. file doesn't exist anymore)
                continue

# Unittests
