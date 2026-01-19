import os
from pathlib import Path
import time
import pwd
import getpass

def purge_old_items(target_dir: Path, age_days: int) -> None:
    """
    Delete files from a specified directory that are older than a given number of days,
    provided those files are owned by the current user.

    Args:
        target_dir: Path, the path to the directory containing target files.
        age_days: int, the number of days beyond which the files are considered old and should be deleted.
    
    Returns:
        None
    """
    # Ensure target directory exists and is a directory
    if not target_dir.exists():
        raise FileNotFoundError(f"Directory not found: {target_dir}")
    if not target_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {target_dir}")
    
    # Get current user's UID
    current_username = getpass.getuser()
    try:
        current_uid = pwd.getpwnam(current_username).pw_uid
    except KeyError:
        raise RuntimeError(f"Could not determine UID for current user: {current_username}")
    
    # Calculate cutoff time (now - age_days)
    cutoff_time = time.time() - (age_days * 24 * 60 * 60)
    
    # Iterate through all items in the directory
    for item in target_dir.iterdir():
        # Skip if it's not a file (e.g., subdirectories, links)
        if not item.is_file():
            continue
            
        try:
            # Get file stat to check ownership and modification time
            stat_info = item.stat()
            
            # Verify file is owned by current user
            if stat_info.st_uid != current_uid:
                continue
                
            # Check if file is older than the cutoff time
            if stat_info.st_mtime < cutoff_time:
                # Safely delete the file
                item.unlink()
                
        except (OSError, PermissionError) as e:
            # Skip files that can't be accessed or deleted
            # This prevents the function from crashing on permission errors
            continue

# Unittests
