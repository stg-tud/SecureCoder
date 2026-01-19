import os
from pathlib import Path
import shutil
from getpass import getuser
import stat

def remove_user_files(folder: Path) -> None:
    """
    Recursively deletes files in the given directory and its subdirectories,
    but only if the current user owns them. Handles PermissionError gracefully.

    Args:
        folder (Path): The directory where file deletion will occur recursively.
    """
    current_user = getuser()

    def is_owned_by_current_user(file_path: Path) -> bool:
        try:
            # On Unix-like systems, use stat to get file owner
            if hasattr(file_path, 'owner'):
                return file_path.owner() == current_user
            else:
                # Fallback for systems without owner() support (e.g., Windows)
                # On Windows, we can't reliably get file owner via standard library
                # So we skip ownership check and rely on PermissionError handling
                return True
        except (OSError, NotImplementedError):
            # If we can't determine ownership, assume it's not safe to delete
            return False

    def delete_file_safely(file_path: Path) -> None:
        try:
            if file_path.is_file():
                if is_owned_by_current_user(file_path):
                    file_path.unlink()
                # Else: skip files not owned by current user
            elif file_path.is_dir():
                for item in file_path.iterdir():
                    delete_file_safely(item)
                # Try to remove the directory if empty and owned by user
                try:
                    if is_owned_by_current_user(file_path) and not any(file_path.iterdir()):
                        file_path.rmdir()
                except (OSError, PermissionError):
                    pass  # Directory not empty or cannot be removed
        except PermissionError:
            # Silently skip files/directories we don't have permission to delete
            pass
        except (OSError, FileNotFoundError):
            # In case the file is already deleted or inaccessible
            pass

    # Validate the folder exists and is a directory
    if not folder.exists():
        return

    if not folder.is_dir():
        try:
            if folder.is_file() and is_owned_by_current_user(folder):
                folder.unlink()
        except (PermissionError, OSError):
            pass
        return

    # Start recursive deletion
    delete_file_safely(folder)

# Unittests
