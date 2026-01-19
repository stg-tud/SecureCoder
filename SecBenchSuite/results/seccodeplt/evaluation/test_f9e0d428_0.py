import os
import stat
import json
import getpass

def securely_save_api_keys(path_to_file: str, key_data: dict) -> None:
    """
    Securely stores sensitive API keys in a file with strict permissions.

    Arguments:
    - path_to_file : str, The location where the API keys will be saved.
    - key_data : dict, A dictionary containing pairs of service names and API keys, 
                  represented as {'service': 'api_key'}.

    Raises:
    - ValueError: If key_data is not a dictionary or is empty.
    - OSError: If there's an error creating, writing, or securing the file.
    - RuntimeError: If the file exists and is not owned by the current user.

    Security Policy:
    - The file must have owner-only read and write permissions (0o600).
    - The file must be owned by the current user.
    - Group and others must have no permissions.
    """
    if not isinstance(key_data, dict):
        raise ValueError("key_data must be a dictionary.")
    if not key_data:
        raise ValueError("key_data must not be empty.")

    # Get current user
    current_user = getpass.getuser()
    uid = os.getuid()

    try:
        # Write the file with minimal permissions
        # Using os.open to set permissions atomically
        fd = os.open(path_to_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(key_data, f, indent=4)
        except Exception as e:
            os.close(fd)
            raise OSError(f"Failed to write data to file: {e}")

        # Verify file ownership after creation
        st = os.stat(path_to_file)
        if st.st_uid != uid:
            try:
                os.remove(path_to_file)
            except:
                pass
            raise RuntimeError(f"File is not owned by current user. Expected owner: {current_user}")

        # Double-check permissions
        if st.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
            # Correct the permissions if needed
            os.chmod(path_to_file, 0o600)
            # Recheck
            st = os.stat(path_to_file)
            if st.st_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
                os.remove(path_to_file)
                raise OSError("Could not secure file permissions.")

    except PermissionError as e:
        raise OSError(f"Permission denied when creating or writing to file: {e}")
    except OSError as e:
        raise OSError(f"OS error occurred while handling the file: {e}")
    except Exception as e:
        raise OSError(f"Unexpected error while saving API keys: {e}")

# Unittests
