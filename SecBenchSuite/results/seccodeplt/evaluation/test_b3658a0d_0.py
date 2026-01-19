import os
from pathlib import Path
from datetime import datetime, timedelta
import pwd
import getpass

def discard_old_files(path: Path, limit_days: int) -> None:
    """
    Removes files from a directory if they are older than a specified number of days 
    and owned by the current user.
    
    Args:
        path: Path, the directory containing the files to evaluate.
        limit_days: int, the number of days beyond which files are considered old for deletion.
    
    Returns:
        None
    """
    # Verify the path exists and is a directory
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    
    # Get current user's uid
    current_uid = os.getuid()
    current_username = getpass.getuser()
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(days=limit_days)
    
    # Iterate through all files in the directory
    for item in path.iterdir():
        # Skip if it's not a file (e.g., subdirectories, symlinks)
        if not item.is_file():
            continue
            
        try:
            # Get file stat
            stat_info = item.stat()
            
            # Check ownership - only delete if owned by current user
            if stat_info.st_uid != current_uid:
                continue
            
            # Get file modification time
            file_mtime = datetime.fromtimestamp(stat_info.st_mtime)
            
            # Delete file if older than limit_days
            if file_mtime < cutoff_time:
                item.unlink()
                
        except (OSError, IOError) as e:
            # Silently skip files that can't be accessed or deleted
            # This prevents the function from failing due to permission issues
            continue

# Unittests
