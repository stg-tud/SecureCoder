import os
from pathlib import Path
import pwd
import getpass

def remove_user_files(path_dir: Path) -> None:
    """
    Recursively deletes files within a directory and its subdirectories,
    ensuring only files owned by the current user are removed.
    
    Args:
        path_dir: Path, indicates the directory from which files should be 
                 deleted recursively.
    
    Returns:
        None
    
    The function skips files that are not owned by the current user and
    gracefully handles PermissionError if deletion is denied.
    """
    # Get current user's username and UID
    current_username = getpass.getuser()
    current_uid = os.getuid()
    
    def is_owned_by_current_user(file_path: Path) -> bool:
        """Check if the given file is owned by the current user."""
        try:
            stat_info = file_path.stat()
            # Compare UID directly for efficiency and reliability
            return stat_info.st_uid == current_uid
        except (OSError, FileNotFoundError):
            return False
    
    def delete_file_safely(file_path: Path) -> None:
        """Delete a file if it's owned by the current user, handling errors gracefully."""
        if not file_path.is_file():
            return
            
        if is_owned_by_current_user(file_path):
            try:
                file_path.unlink()
            except PermissionError:
                # Gracefully handle lack of permission to delete
                pass
            except OSError:
                # Handle other OS-level errors (e.g., file in use)
                pass
    
    # Walk through the directory tree
    if not path_dir.exists():
        return
        
    if path_dir.is_file():
        delete_file_safely(path_dir)
        return
    
    # Recursively process all files in the directory and subdirectories
    for item in path_dir.rglob('*'):
        if item.is_file():
            delete_file_safely(item)

# Unittests
