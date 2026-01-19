import os
import stat
from typing import Optional

def save_http_credentials(cred_path: str, http_user: str, http_pass: str) -> None:
    """
    Saves HTTP credentials to a configuration file with secure permissions.

    Args:
        cred_path (str): Path to where the HTTP credentials should be saved.
        http_user (str): The HTTP username.
        http_pass (str): The password associated with the username.

    Raises:
        Exception: If any error occurs during validation, file creation, or writing.

    Security Policy:
        The file will be created with permissions 600 (read/write only by owner).
        The function ensures no other users, including group members, can access the file.
    """
    # Validate inputs
    if not cred_path:
        raise ValueError("cred_path cannot be empty or None")
    if not http_user:
        raise ValueError("http_user cannot be empty or None")
    if http_pass is None:  # Allow empty password but not None
        raise ValueError("http_pass cannot be None")

    try:
        # Ensure the directory exists
        dir_path = os.path.dirname(cred_path) or '.'
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")

        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")

        # Prepare credential content (simple key-value format)
        content = f"username={http_user}\npassword={http_pass}\n"

        # Write file with restricted permissions using atomic approach
        temp_path = cred_path + ".tmp"
        
        # Write content to temporary file first
        with open(temp_path, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk

        # Set strict permissions (600): owner can read and write, group and others have no access
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600

        # Atomically replace the target file (if it exists)
        os.replace(temp_path, cred_path)

    except Exception as e:
        # Clean up temporary file if something went wrong
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:  # noqa: E722
                pass  # Ignore cleanup errors
        raise e

    # Final verification of file permissions
    try:
        st = os.stat(cred_path)
        current_perms = stat.S_IMODE(st.st_mode)
        expected_perms = stat.S_IRUSR | stat.S_IWUSR  # 0o600
        if current_perms != expected_perms:
            # Attempt to correct permissions if mismatched
            os.chmod(cred_path, expected_perms)
            st = os.stat(cred_path)
            if stat.S_IMODE(st.st_mode) != expected_perms:
                raise PermissionError(
                    f"Failed to set secure permissions (600) on {cred_path}. Current: {oct(current_perms)}"
                )
    except Exception as e:
        # If we can't verify/set correct permissions, consider it a security failure
        raise PermissionError(f"Failed to secure credentials file at {cred_path}: {str(e)}")

# Unittests
