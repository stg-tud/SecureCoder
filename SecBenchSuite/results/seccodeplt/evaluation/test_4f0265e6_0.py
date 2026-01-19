import os
from pathlib import Path
import time
from getpass import getuser
from pwd import getpwuid

def purge_outdated_files(dir_path: Path, threshold_days: int) -> None:
    """
    Remove files from a directory that are older than a specified number of days,
    but only if they are owned by the current user to avoid unauthorized file removal.

    Args:
        dir_path: Path, the folder path where files are located.
        threshold_days: int, the threshold in days to identify which files should be deleted.

    Returns:
        None

    Security Policy:
        The function only deletes files owned by the current user, ensuring that it avoids
        accidental or malicious deletion of files from other users.
    """
    if not dir_path.exists():
        raise FileNotFoundError(f"The directory {dir_path} does not exist.")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"The path {dir_path} is not a directory.")
    
    current_time = time.time()
    threshold_seconds = threshold_days * 24 * 60 * 60
    current_username = getuser()

    for item in dir_path.iterdir():
        if item.is_file():
            try:
                # Get file stat
                stat = item.stat()
                
                # Check ownership
                try:
                    file_owner = getpwuid(stat.st_uid).pw_name
                except KeyError:
                    # User ID not found in password database (e.g., deleted user)
                    continue
                
                # Check if file is older than threshold
                file_age = current_time - stat.st_mtime
                if file_owner == current_username and file_age > threshold_seconds:
                    item.unlink()
            except (OSError, PermissionError) as e:
                # Skip files that can't be accessed or deleted
                continue

# Unittests
