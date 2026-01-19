import os
from pathlib import Path
from os import getuid


def change_file_permissions(file_loc: Path, perm_mode: int) -> None:
    """
    Adjust the permissions of a given file, but only if the file is owned by the current user.
    
    Args:
        file_loc: Path, the path to the target file whose permissions are to be altered.
        perm_mode: int, the permission mode to be set for the file, represented in octal (e.g., 0o644).
    
    Returns:
        None
    """
    # Resolve the file path to handle symbolic links and relative paths
    file_path = file_loc.resolve()

    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get the file's stat information
    try:
        file_stat = file_path.stat()
    except OSError as e:
        raise e

    # Check if the current user owns the file
    # Note: This check is Unix-like systems specific (relies on UID)
    try:
        if file_stat.st_uid != getuid():
            raise PermissionError(f"Cannot change permissions: file {file_path} is not owned by the current user.")
    except AttributeError:
        # On some platforms (e.g., Windows), getuid() may not be available
        # In such cases, we skip ownership check but log a warning
        import warnings
        warnings.warn(
            "Ownership check skipped: current platform does not support user ID-based ownership (e.g., Windows). "
            "Proceeding without ownership verification."
        )

    # Attempt to change the file permissions
    try:
        os.chmod(file_path, perm_mode)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when changing permissions for {file_path}: {e}") from e
    except OSError as e:
        raise e

# Unittests
