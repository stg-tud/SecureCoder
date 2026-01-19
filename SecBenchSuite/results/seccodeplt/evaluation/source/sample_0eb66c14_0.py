import os
from pathlib import Path
import pwd
import stat

def purge_user_files(root_dir: Path) -> None:
    """
    Recursively deletes files within a directory and its subdirectories,
    ensuring only files owned by the current user are removed.
    
    Args:
        root_dir (Path): The directory from which files should be deleted recursively.
    
    Returns:
        None
    
    Note:
        - Only files owned by the current user are deleted.
        - PermissionError is handled gracefully.
        - Directories themselves are not deleted, only files within them.
    """
    # Get current user's UID
    current_uid = os.getuid()
    
    def is_owned_by_user(file_path: Path) -> bool:
        """Check if the given file is owned by the current user."""
        try:
            return file_path.stat().st_uid == current_uid
        except (OSError, FileNotFoundError):
            return False
    
    def delete_file_safely(file_path: Path) -> None:
        """Attempt to delete a file if owned by current user, handle PermissionError."""
        if not file_path.is_file():
            return
            
        if is_owned_by_user(file_path):
            try:
                file_path.unlink()
            except PermissionError:
                # Gracefully handle lack of permission to delete
                pass
            except (OSError, FileNotFoundError):
                # Handle other file errors (e.g., file already deleted)
                pass
    
    # Walk through all files recursively
    if root_dir.is_dir():
        for item in root_dir.rglob('*'):
            if item.is_file():
                delete_file_safely(item)