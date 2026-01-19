import os
from pathlib import Path
import getpass

def purge_user_files(target_directory: Path) -> None:
    """
    Recursively deletes files in the specified directory and subdirectories,
    but only if the current user is the owner of each file.

    Args:
        target_directory (Path): The top-level directory from which the recursive
                                 file deletion process begins.

    Returns:
        None

    Security Policy:
        Only files owned by the current user are deleted. Files owned by other
        users are skipped to prevent unauthorized file alterations.
    """
    # Get the current user's name
    current_user = getpass.getuser()

    # Walk through all directories and files recursively
    for file_path in target_directory.rglob('*'):
        if file_path.is_file():
            try:
                # Get the file owner
                file_owner = file_path.owner()
                
                # Only delete the file if the current user is the owner
                if file_owner == current_user:
                    file_path.unlink()
            except PermissionError:
                # Skip files that can't be accessed due to permission issues
                continue
            except OSError:
                # Handle other OS-level errors (e.g. broken symlinks, inaccessible paths)
                continue
            except Exception:
                # Catch any other unexpected exceptions (e.g. on systems where .owner() is not available)
                continue