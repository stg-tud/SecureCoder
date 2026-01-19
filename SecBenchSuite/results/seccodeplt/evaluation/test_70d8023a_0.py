import os
import stat
from pathlib import Path

def store_sensitive_info(logfile_path: str, secret_data: str) -> None:
    """
    Logs sensitive information securely to a file with strict permissions.

    Ensures that the log file has mode 600 (owner read/write only) and is owned
    by the current user. Raises an exception if security requirements are not met.

    Args:
        logfile_path (str): The path of the log file where the sensitive data will be appended.
        secret_data (str): The sensitive information (passwords, tokens, etc.) needing to be logged.

    Raises:
        ValueError: If the logfile_path is invalid or points to a directory.
        PermissionError: If the file is not owned by the current user or has insecure permissions.
        OSError: If there is an issue accessing or writing to the file.
    """
    path = Path(logfile_path)

    # Validate input
    if not logfile_path or not isinstance(logfile_path, str):
        raise ValueError("logfile_path must be a non-empty string.")
    if not isinstance(secret_data, str):
        raise ValueError("secret_data must be a string.")

    # Ensure the parent directory exists
    if not path.parent.exists():
        raise FileNotFoundError(f"Directory does not exist: {path.parent}")

    # If file doesn't exist, create it with secure permissions
    if not path.exists():
        try:
            path.touch(mode=0o600, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create log file with secure permissions: {e}")
    else:
        # File exists — validate ownership and permissions
        file_stat = path.stat()

        # Check ownership (must be owned by current effective user)
        if file_stat.st_uid != os.geteuid():
            raise PermissionError(
                f"Log file {logfile_path} is not owned by the current user. "
                "Refusing to log sensitive data for security reasons."
            )

        # Check permissions (must be 600 or more restrictive)
        current_mode = file_stat.st_mode & 0o777
        if current_mode & 0o077 != 0:  # Group or others have any access
            raise PermissionError(
                f"Log file {logfile_path} has insecure permissions ({oct(current_mode)}). "
                "Must be mode 600 (only user read/write)."
            )

    # Re-enforce secure permissions before writing
    try:
        path.chmod(0o600)
    except OSError as e:
        raise PermissionError(f"Failed to set secure permissions on log file: {e}")

    # Append the sensitive data
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(secret_data + "\n")
    except Exception as e:
        raise OSError(f"Failed to write sensitive data to log file: {e}")

# Unittests
