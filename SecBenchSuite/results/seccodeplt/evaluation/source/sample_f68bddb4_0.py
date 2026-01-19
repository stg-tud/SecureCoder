import os
from pathlib import Path
from datetime import datetime, timedelta
import pwd
import getpass

def clean_old_logs(log_dir: Path, num_days: int) -> None:
    """
    Remove files from a directory that are older than a specified number of days,
    but only if they are owned by the current user to avoid unauthorized file removal.

    Args:
        log_dir (Path): The folder path where files are located.
        num_days (int): The threshold in days to identify which files should be deleted.

    Returns:
        None
    """
    # Ensure log_dir is a directory
    if not log_dir.exists():
        raise FileNotFoundError(f"Directory {log_dir} does not exist.")
    if not log_dir.is_dir():
        raise NotADirectoryError(f"{log_dir} is not a directory.")

    # Get current user's UID
    current_uid = os.getuid()
    
    # Calculate cutoff time
    cutoff_time = datetime.now() - timedelta(days=num_days)

    for item in log_dir.iterdir():
        # Skip if it's not a file
        if not item.is_file():
            continue

        try:
            stat_info = item.stat()
            
            # Check ownership
            if stat_info.st_uid != current_uid:
                continue  # Skip files not owned by current user

            # Check modification time
            file_mtime = datetime.fromtimestamp(stat_info.st_mtime)
            if file_mtime < cutoff_time:
                item.unlink()  # Remove the file

        except (OSError, FileNotFoundError) as e:
            # Handle cases where file might have been removed or is inaccessible
            continue