import os
import stat
import json
from typing import Dict


def secure_key_storage(path_to_file: str, creds: Dict[str, str]) -> None:
    """
    Securely stores API keys in a file with strict permissions.

    The file is created with owner-only read and write permissions (0o600).
    Before writing, it checks that the current user is the owner of the file
    (if it exists), or ensures ownership after creation.

    Args:
        path_to_file (str): The path to the file where the API keys should be saved.
        creds (dict): A dictionary containing service names as keys and API keys as values.

    Raises:
        PermissionError: If the file is owned by a different user or permissions cannot be set.
        OSError: If there's an error during file operations.
        TypeError: If creds is not a dictionary.
    """
    if not isinstance(creds, dict):
        raise TypeError("creds must be a dictionary")

    # Expand user and resolve path
    path_to_file = os.path.abspath(os.path.expanduser(path_to_file))

    # Check if file exists
    file_exists = os.path.exists(path_to_file)

    # If file exists, check ownership
    if file_exists:
        file_stat = os.stat(path_to_file)
        if file_stat.st_uid != os.getuid():
            raise PermissionError(
                f"File {path_to_file} is not owned by the current user. "
                f"Current UID: {os.getuid()}, File UID: {file_stat.st_uid}"
            )

    try:
        # Write the credentials to the file with restricted permissions
        with open(path_to_file, 'w') as f:
            json.dump(creds, f, indent=4)

        # Set permissions to owner read/write only (0o600)
        os.chmod(path_to_file, stat.S_IRUSR | stat.S_IWUSR)

        # Double-check ownership after creation/modification
        final_stat = os.stat(path_to_file)
        if final_stat.st_uid != os.getuid():
            # Try to change ownership if possible (requires appropriate privileges)
            try:
                os.chown(path_to_file, os.getuid(), -1)
            except PermissionError:
                # If we can't change ownership, clean up and raise error
                os.remove(path_to_file)
                raise PermissionError(
                    f"Unable to set ownership of {path_to_file} to current user."
                )

        # Final verification of permissions
        if final_stat.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
            # Fix permissions if they were somehow changed between chmod and stat
            os.chmod(path_to_file, stat.S_IRUSR | stat.S_IWUSR)

    except PermissionError:
        raise
    except OSError as e:
        raise OSError(f"Failed to write or secure API keys file: {e.strerror}") from e
    except Exception as e:
        raise Exception(f"Unexpected error during secure key storage: {str(e)}") from e

# Unittests
