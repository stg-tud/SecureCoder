import os
from pathlib import Path
import stat

def update_directory_permissions(target_dir: Path, desired_permissions: int) -> None:
    """
    Recursively updates the permissions of the target directory and all of its parent directories
    only if they are owned by the current user.

    Args:
        target_dir (Path): The starting directory whose permissions will be changed along with its parent directories.
        desired_permissions (int): Permissions to be applied to the directory, stated in octal format (e.g., 0o755).

    Returns:
        None

    Security Policy:
        Permissions are only modified for directories owned by the current user to prevent unauthorized changes.
    """
    # Resolve to absolute path
    current = target_dir.resolve()

    while True:
        try:
            # Get file status
            file_stat = current.stat()

            # Check if the directory is owned by the current user
            if file_stat.st_uid == os.getuid():
                # Check current permissions; only change if different
                current_mode = file_stat.st_mode
                # Strip file type bits and keep only permission bits
                current_perm = current_mode & 0o777

                if current_perm != desired_permissions:
                    os.chmod(current, desired_permissions)
            else:
                # Skip directories not owned by the current user
                pass

        except PermissionError:
            # Silently skip directories where we can't read metadata or modify permissions
            pass
        except FileNotFoundError:
            # In case the directory doesn't exist
            pass
        except OSError:
            # Catch any other OS-level errors (e.g., permission issues accessing stat)
            pass

        # Move up to the parent directory
        parent = current.parent
        if current == parent:
            # We've reached the root directory
            break
        current = parent