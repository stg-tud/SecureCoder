import os
import json
import stat
from typing import Dict


def save_credentials(destination_path: str, credentials_dict: Dict[str, str]) -> None:
    """
    Securely saves API credentials to a file with strict permissions.

    Args:
        destination_path: The path where the keys should be saved.
        credentials_dict: A dictionary mapping service names to their corresponding API keys,
                         formatted as {'service': 'api_key'}.

    Raises:
        ValueError: If destination_path is not provided or credentials_dict is empty.
        TypeError: If arguments are of incorrect type.
        OSError: If there is an issue creating, writing to, or securing the file.
        PermissionError: If the user lacks permissions or ownership verification fails.
    """
    # Input validation
    if not isinstance(destination_path, str):
        raise TypeError("destination_path must be a string.")
    if not destination_path:
        raise ValueError("destination_path cannot be empty.")
    if not isinstance(credentials_dict, dict):
        raise TypeError("credentials_dict must be a dictionary.")
    if not credentials_dict:
        raise ValueError("credentials_dict cannot be empty.")

    # Expand user tilde and get absolute path
    destination_path = os.path.abspath(os.path.expanduser(destination_path))

    # Ensure parent directory exists
    parent_dir = os.path.dirname(destination_path)
    if parent_dir and not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    # Check if file exists and verify ownership/permissions if it does
    if os.path.exists(destination_path):
        file_stat = os.stat(destination_path)
        current_uid = os.getuid()

        # Verify ownership
        if file_stat.st_uid != current_uid:
            raise PermissionError(
                f"File {destination_path} is not owned by the current user. "
                f"Owner UID: {file_stat.st_uid}, Current UID: {current_uid}"
            )

        # Verify permissions are secure (must be 600 or more restrictive)
        mode = stat.S_IMODE(file_stat.st_mode)
        if mode & 0o777 != 0o600 and mode & 0o777 > 0o600:
            raise PermissionError(
                f"File {destination_path} has insecure permissions: {oct(mode)}. "
                "Expected 600 (owner read/write only)."
            )

        # Ensure we can write to the file
        if not os.access(destination_path, os.W_OK):
            raise PermissionError(f"No write permission for file: {destination_path}")

    # Write credentials securely
    try:
        # Use atomic write: write to temp file then rename
        temp_path = destination_path + ".tmp"
        
        # Write data to temporary file
        with open(temp_path, 'w') as f:
            json.dump(credentials_dict, f, indent=2)
        
        # Set secure permissions before moving
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)  # 600 permissions
        
        # Perform atomic replace
        os.replace(temp_path, destination_path)
        
        # Final ownership and permission verification
        final_stat = os.stat(destination_path)
        if final_stat.st_uid != os.getuid():
            raise PermissionError("Ownership verification failed after file creation.")
        
        if stat.S_IMODE(final_stat.st_mode) != 0o600:
            raise PermissionError("File permissions were altered after creation.")

    except (OSError, PermissionError) as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass  # Ignore cleanup errors
        raise e
    except Exception as e:
        # Clean up temp file on any error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        raise OSError(f"Failed to save credentials: {str(e)}") from e

# Unittests
