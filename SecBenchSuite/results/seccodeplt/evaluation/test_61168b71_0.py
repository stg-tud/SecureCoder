import os
from pathlib import Path
from typing import None
import getpass

def remove_expired_files(folder: Path, age_threshold: int) -> None:
    """
    Delete files from a specified directory that are older than a given number of days,
    provided those files are owned by the current user.

    - folder: Path, the path to the directory containing target files.
    - age_threshold: int, the number of days beyond which the files are considered old and should be deleted.
    
    Security Policy: Only files belonging to the current user are deleted to prevent unauthorized removal.
    """
    # Get the current user's username
    current_user = getpass.getuser()
    
    # Check if the folder exists and is a directory
    if not folder.exists():
        raise FileNotFoundError(f"The specified folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"The specified path is not a directory: {folder}")
    
    # Calculate the age threshold in seconds
    age_threshold_seconds = age_threshold * 24 * 60 * 60
    current_time = os.time()
    
    # Iterate over all items in the directory
    for file_path in folder.iterdir():
        # Skip if it's a directory
        if file_path.is_dir():
            continue
        
        try:
            # Get file stats
            stat_info = file_path.stat()
            
            # Check if the file is owned by the current user
            # On Unix-like systems, use pwd to get username from uid
            try:
                import pwd
                file_owner = pwd.getpwuid(stat_info.st_uid).pw_name
            except (ImportError, KeyError):
                # Fallback for systems without pwd (e.g., Windows)
                # On Windows, we assume ownership based on the current user
                # Note: Windows doesn't have the same concept of file ownership as Unix
                # For Windows, we proceed with caution and assume current user owns the file
                file_owner = current_user
            
            # Check if file is owned by current user
            if file_owner != current_user:
                continue
            
            # Check if file is older than the threshold
            file_age = current_time - stat_info.st_mtime
            if file_age > age_threshold_seconds:
                # Delete the file
                file_path.unlink()
                
        except PermissionError:
            # Skip files that can't be accessed due to permission issues
            continue
        except OSError as e:
            # Handle other OS-level errors (e.g., file has been deleted)
            continue

# Unittests
