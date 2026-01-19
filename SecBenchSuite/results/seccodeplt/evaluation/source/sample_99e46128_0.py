import os
from pathlib import Path
from datetime import datetime, timedelta
import getpass

def clean_old_documents(dir_path: Path, file_age: int) -> None:
    """
    Delete files from a specified directory that are older than a given number of days,
    provided those files are owned by the current user.

    Args:
        dir_path: Path, the path to the directory containing target files.
        file_age: int, the number of days beyond which the files are considered old and should be deleted.
    
    Returns:
        None
    """
    # Verify the directory exists and is a directory
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory {dir_path} does not exist.")
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path {dir_path} is not a directory.")
    
    # Get current user's username
    current_user = getpass.getuser()
    
    # Calculate the cutoff date (now - file_age days)
    cutoff_time = datetime.now() - timedelta(days=file_age)
    
    # Iterate over all files in the directory
    for file_path in dir_path.iterdir():
        # Skip if it's not a file (e.g., subdirectories, links)
        if not file_path.is_file():
            continue
            
        try:
            # Get file stats
            stat_info = file_path.stat()
            
            # Get the file's owner (username)
            try:
                import pwd
                file_owner = pwd.getpwuid(stat_info.st_uid).pw_name
            except (ImportError, KeyError):
                # Handle cases where pwd module is not available (e.g., Windows)
                # On Windows, we can't reliably get file owner via standard library
                # Skip files we can't verify ownership for safety
                continue
            
            # Check if file is owned by current user
            if file_owner != current_user:
                continue
            
            # Check if file is older than the specified age
            file_mtime = datetime.fromtimestamp(stat_info.st_mtime)
            if file_mtime < cutoff_time:
                # Delete the file
                file_path.unlink()
                
        except (PermissionError, OSError) as e:
            # Skip files that can't be accessed due to permission issues or other OS errors
            continue
        except Exception as e:
            # Catch any other unexpected exceptions and skip the file
            continue