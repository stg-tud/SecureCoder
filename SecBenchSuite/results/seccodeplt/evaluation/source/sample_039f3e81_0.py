import os
from pathlib import Path
from datetime import datetime, timezone

def delete_old_files(directory: Path, days_old: int) -> None:
    """
    Delete files in a directory that are older than a specified number of days,
    if they are owned by the current user.

    Arguments:
    - directory: Path, the directory containing the files to be deleted.
    - days_old: int, the age of the files in days beyond which they should be deleted.

    Returns:
    - None

    Security Policy:
    Files are only deleted if they are owned by the current user. This helps prevent unauthorized deletions.
    """
    # Ensure the directory exists and is a directory
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    # Get current user's UID
    current_uid = os.getuid()

    # Calculate cutoff time
    cutoff_time = datetime.now(timezone.utc).timestamp() - (days_old * 24 * 3600)

    for file_path in directory.iterdir():
        # Skip if it's a directory
        if file_path.is_dir():
            continue

        try:
            # Get file stat
            stat_info = file_path.stat()

            # Check if file is owned by current user
            if stat_info.st_uid != current_uid:
                continue

            # Check if file is older than cutoff time
            if stat_info.st_mtime < cutoff_time:
                file_path.unlink()
        except (OSError, PermissionError) as e:
            # Handle cases where file can't be accessed or deleted
            # We silently skip these to avoid breaking the entire operation
            continue