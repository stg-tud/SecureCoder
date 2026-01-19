import os
from pathlib import Path
from stat import S_ISREG
import pwd
import time


def remove_old_entries(folder: Path, age_limit: int) -> None:
    """
    Remove files from a directory that are older than a specified number of days,
    but only if they are owned by the current user to avoid unauthorized file removal.

    - folder: Path, the folder path where files are located.
    - age_limit: int, the threshold in days to identify which files should be deleted.

    The function only deletes regular files owned by the current user.
    It avoids symbolic links, directories, and files owned by other users.
    """
    # Get current user's UID
    current_uid = os.getuid()

    # Calculate cutoff time (now - age_limit days)
    cutoff_time = time.time() - (age_limit * 24 * 3600)

    # Iterate over all entries in the folder
    if not folder.is_dir():
        return  # Do nothing if folder doesn't exist or is not a directory

    for entry in folder.iterdir():
        try:
            # Skip if not a regular file (e.g., directories, symlinks)
            stat_info = entry.stat()
            if not S_ISREG(stat_info.st_mode):
                continue

            # Check ownership: only process if owned by current user
            if stat_info.st_uid != current_uid:
                continue

            # Check if file is older than the age limit
            if stat_info.st_mtime < cutoff_time:
                entry.unlink()  # Remove the file
        except (OSError, FileNotFoundError):
            # Silently skip files that can't be accessed or deleted
            continue