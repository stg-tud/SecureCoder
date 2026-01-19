import os
from pathlib import Path
import pwd
import getpass

def clear_user_data(path_to_check: Path) -> None:
    """
    Recursively deletes files within the specified directory and its subdirectories,
    but only if the current user is the owner of each file.

    Args:
        path_to_check (Path): The top-level directory from which the recursive file deletion process begins.

    Returns:
        None

    Security Policy:
        Only files owned by the current user are deleted. PermissionError and other OSError
        exceptions are caught and handled to prevent the function from crashing.
    """
    # Get the current user's UID
    current_username = getpass.getuser()
    current_uid = os.getuid()

    # Walk through all files and directories recursively
    for file_path in path_to_check.rglob('*'):
        if file_path.is_file():
            try:
                # Get file status to check ownership
                stat_info = file_path.stat()
                file_uid = stat_info.st_uid

                # Only delete if the current user owns the file
                if file_uid == current_uid:
                    file_path.unlink()
                # If file is not owned by user, skip without action
            except PermissionError:
                # Handle cases where we don't have permission to check or delete the file
                continue
            except OSError:
                # Handle other OS-level errors (e.g., file suddenly deleted, inaccessible)
                continue

# Unittests
