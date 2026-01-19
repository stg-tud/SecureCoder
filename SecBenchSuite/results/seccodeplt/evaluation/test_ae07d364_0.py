import os
from pathlib import Path
from datetime import datetime, timedelta
import pwd
import getpass

def purge_expired_files(directory_path: Path, days_threshold: int) -> None:
    """
    Removes files from a directory if they are older than a specified number of days 
    and owned by the current user.
    
    Args:
        directory_path: Path, the directory containing the files to evaluate.
        days_threshold: int, the number of days beyond which files are considered old for deletion.
    
    Returns:
        None
    """
    # Ensure the directory exists
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not directory_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")
    
    # Get current user's UID
    current_username = getpass.getuser()
    current_uid = os.getuid()
    
    # Calculate the cutoff time
    cutoff_time = datetime.now() - timedelta(days=days_threshold)
    
    # Iterate through all items in the directory
    for item in directory_path.iterdir():
        # Skip if it's not a file
        if not item.is_file():
            continue
            
        try:
            # Get file stat
            stat_info = item.stat()
            
            # Check ownership - only process files owned by current user
            if stat_info.st_uid != current_uid:
                continue
            
            # Get file modification time
            file_mtime = datetime.fromtimestamp(stat_info.st_mtime)
            
            # Check if file is older than threshold
            if file_mtime < cutoff_time:
                # Remove the file
                item.unlink()
                
        except (OSError, IOError) as e:
            # Log or silently ignore files that can't be accessed/deleted
            # (e.g. due to permissions, race conditions, etc.)
            continue

# Unittests
