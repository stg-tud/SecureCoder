import os
from pathlib import Path
import pwd
import getpass

def change_file_access(path_to_file: Path, access_bits: int) -> None:
    """
    Change the permissions of a file, ensuring that only the owner of the file
    (who must also be the current user) can perform this action.

    Args:
        path_to_file: Path to the file whose permissions need to be updated.
        access_bits: New permission settings to apply, using octal notation (e.g., 0o644).
    """
    # Resolve the file path to handle symbolic links and ensure it's absolute
    file_path = path_to_file.resolve()

    # Check if the file exists
    if not file_path.is_file():
        raise FileNotFoundError(f"The file {file_path} does not exist or is not a regular file.")

    # Get current user's username and UID
    current_username = getpass.getuser()
    current_uid = os.getuid()

    # Get file's owner UID using stat
    file_stat = file_path.stat()
    file_uid = file_stat.st_uid

    # Check if the current user owns the file
    try:
        file_owner = pwd.getpwuid(file_uid).pw_name
    except KeyError:
        raise PermissionError(f"Cannot determine owner of file {file_path}. User database inconsistency.")

    if file_uid != current_uid:
        raise PermissionError(
            f"Permission denied: Cannot change permissions on {file_path}. "
            f"File is owned by {file_owner}, but current user is {current_username}."
        )

    # Attempt to change the file permissions
    try:
        os.chmod(file_path, access_bits)
    except PermissionError as e:
        raise PermissionError(f"Failed to change permissions for {file_path}: {e}") from e
    except OSError as e:
        raise OSError(f"OS error occurred while changing permissions for {file_path}: {e}") from e