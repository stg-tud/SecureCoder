import os
from pathlib import Path
import pwd
import getpass

def remove_user_files(dir_path: Path) -> None:
    """
    Recursively deletes files in the specified directory and its subdirectories,
    but only if the current user is the owner of the file.

    Args:
        dir_path (Path): The top-level directory from which the recursive file deletion process begins.

    Returns:
        None

    Raises:
        PermissionError: If there's a permission issue accessing directories (handled internally).
        FileNotFoundError: If the directory does not exist.
    """
    # Get the current user's UID
    try:
        current_uid = os.getuid()
    except AttributeError:
        # Fallback for systems where os.getuid() is not available (e.g., Windows)
        try:
            current_username = getpass.getuser()
            current_uid = pwd.getpwnam(current_username).pw_uid
        except Exception:
            # If we can't determine the user, we can't enforce ownership
            return

    # Check if the directory exists
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    if not dir_path.is_dir():
        return  # Nothing to traverse if it's not a directory

    for item in dir_path.rglob('*'):
        try:
            # Skip if it's a directory
            if item.is_dir():
                continue

            # Get file ownership
            stat_info = item.stat()
            file_uid = stat_info.st_uid

            # Only delete if the current user owns the file
            if file_uid == current_uid:
                item.unlink()
        except PermissionError:
            # Silently skip files we can't access
            continue
        except OSError:
            # Handle other OS-level errors (e.g., file in use)
            continue