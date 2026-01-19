import os
from pathlib import Path
import pwd
import getpass

def update_file_permissions(target_path: Path, permissions: int) -> None:
    """
    Adjust the permissions of a given file, but only if the file is owned by the current user.
    
    Args:
        target_path (Path): The path to the target file whose permissions are to be altered.
        permissions (int): The permission mode to be set for the file, represented in octal (e.g., 0o644).
    
    Returns:
        None
    """
    # Resolve the path to handle symbolic links and relative paths
    resolved_path = target_path.resolve()

    # Check if the file exists
    if not resolved_path.exists():
        raise FileNotFoundError(f"The file {resolved_path} does not exist.")

    # Get current user's username
    current_user = getpass.getuser()

    try:
        # Get file status
        file_stat = resolved_path.stat()
        
        # Get the owner's username from the file's UID
        try:
            file_owner = pwd.getpwuid(file_stat.st_uid).pw_name
        except KeyError:
            # In case the user ID does not exist in the password database
            file_owner = None

        # Only proceed if the current user owns the file
        if file_owner != current_user:
            raise PermissionError(f"Cannot modify permissions: file {resolved_path} is not owned by user '{current_user}'.")

        # Change the file permissions
        os.chmod(resolved_path, permissions)

    except PermissionError:
        # Re-raise PermissionError to be handled by caller if needed
        raise
    except OSError as e:
        # Handle other OS-related errors (e.g., read-only filesystem)
        raise OSError(f"Failed to update permissions for {resolved_path}: {e}") from e

# Unittests
