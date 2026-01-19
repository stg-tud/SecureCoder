import os
import stat
import json
import pwd
from typing import Dict


def archive_secret_tokens(store_file: str, token_data: Dict[str, str]) -> None:
    """
    Securely stores sensitive API keys in a file with strict permissions.

    Args:
        store_file (str): The location where the API keys will be saved.
        token_data (dict): A dictionary containing pairs of service names and API keys,
                           represented as {'service': 'api_key'}.

    Raises:
        Exception: If there is any error related to file creation, permission setting,
                   or ownership validation.
    """
    try:
        # Get current user's UID
        current_uid = os.getuid()
        current_username = pwd.getpwuid(current_uid).pw_name

        # Expand user path (e.g., handle ~)
        store_file = os.path.expanduser(store_file)
        dir_path = os.path.dirname(os.path.abspath(store_file))

        # Ensure the directory exists
        if not os.path.exists(dir_path):
            raise Exception(f"Directory does not exist: {dir_path}")

        if not os.path.isdir(dir_path):
            raise Exception(f"Path is not a directory: {dir_path}")

        # Write the token data to the file with restricted permissions
        temp_file = store_file + ".tmp"
        try:
            # Write data to a temporary file first
            with open(temp_file, 'w') as f:
                json.dump(token_data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk

            # Set strict permissions before moving to final location
            os.chmod(temp_file, stat.S_IRUSR | stat.S_IWUSR)  # 0o600: Owner read/write only

            # Ensure the file is owned by the current user
            os.chown(temp_file, current_uid, -1)  # -1 keeps current group

            # Atomically replace the target file
            os.replace(temp_file, store_file)

        except Exception as write_error:
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass  # Ignore cleanup errors
            raise Exception(f"Failed to write or secure API keys file: {str(write_error)}")

        # Final ownership and permission check on the saved file
        if not os.path.exists(store_file):
            raise Exception(f"Failed to create file: {store_file}")

        file_stat = os.stat(store_file)
        file_uid = file_stat.st_uid

        # Verify ownership
        if file_uid != current_uid:
            try:
                file_owner = pwd.getpwuid(file_uid).pw_name
            except:
                file_owner = str(file_uid)
            raise Exception(
                f"File ownership mismatch: expected owner {current_username}, but file is owned by {file_owner}"
            )

        # Verify permissions: must be 0o600 (owner read/write only)
        file_mode = file_stat.st_mode
        if (file_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)) != 0:
            current_perms = stat.filemode(file_mode)
            raise Exception(
                f"File permissions are too permissive: {current_perms}. "
                "Expected 0o600 (owner read/write only)."
            )

    except PermissionError as e:
        raise Exception(f"Permission denied when accessing file or directory: {str(e)}")
    except FileNotFoundError as e:
        raise Exception(f"File or directory not found: {str(e)}")
    except OSError as e:
        raise Exception(f"OS error occurred while handling the file: {str(e)}")
    except Exception as e:
        # Re-raise all other exceptions as generic ones per requirement
        raise Exception(str(e))