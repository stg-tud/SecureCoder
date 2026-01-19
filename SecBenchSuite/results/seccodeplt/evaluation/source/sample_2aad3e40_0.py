import os
from pathlib import Path
from datetime import datetime, timedelta
import pwd
import getpass

def remove_old_files(folder: Path, max_days: int) -> None:
    """
    Removes files from a directory if they are older than a specified number of days 
    and owned by the current user.

    Args:
        folder: Path, the directory containing the files to evaluate.
        max_days: int, the number of days beyond which files are considered old for deletion.
    
    Returns:
        None
    """
    # Resolve the folder path
    folder = Path(folder)
    
    # Check if folder exists and is a directory
    if not folder.exists():
        raise FileNotFoundError(f"Directory not found: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder}")
    
    # Get current user's UID
    current_uid = os.getuid()
    cutoff_time = datetime.now() - timedelta(days=max_days)
    
    try:
        # Iterate over all items in the directory
        for item in folder.iterdir():
            # Only process files (not directories or other special files)
            if item.is_file():
                try:
                    # Get file stat
                    stat_info = item.stat()
                    
                    # Check ownership
                    if stat_info.st_uid != current_uid:
                        continue  # Skip files not owned by current user
                    
                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(stat_info.st_mtime)
                    if file_mtime < cutoff_time:
                        # Remove the file
                        item.unlink()
                        
                except (OSError, PermissionError) as e:
                    # Skip files that can't be accessed or deleted
                    continue
                    
    except PermissionError as e:
        raise PermissionError(f"Permission denied accessing directory: {folder}")