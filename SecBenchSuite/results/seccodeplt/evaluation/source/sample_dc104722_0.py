import os
import stat
from pathlib import Path

def record_sensitive_content(path_to_logfile: str, confidential_data: str) -> None:
    """
    Logs sensitive content securely to a file with strict permissions.

    Args:
        path_to_logfile (str): The path of the log file where the sensitive data will be appended.
        confidential_data (str): The sensitive information (passwords, tokens, etc.) needing to be logged.

    Raises:
        ValueError: If the file permissions are insecure or ownership is not correct.
        OSError: If there is an issue accessing or modifying the file.
        FileNotFoundError: If the file or parent directory does not exist and cannot be created.
    """
    path = Path(path_to_logfile)

    # Ensure the parent directory exists
    if not path.parent.exists():
        raise FileNotFoundError(f"Parent directory does not exist: {path.parent}")

    # Create the file if it doesn't exist
    if not path.exists():
        try:
            path.touch(mode=0o600, exist_ok=True)
        except Exception as e:
            raise OSError(f"Failed to create log file: {e}")

    # Verify file ownership
    file_stat = path.stat()
    current_uid = os.getuid()
    if file_stat.st_uid != current_uid:
        raise ValueError(
            f"Log file {path_to_logfile} is not owned by the current user. "
            f"Expected UID: {current_uid}, Actual UID: {file_stat.st_uid}"
        )

    # Verify file permissions (must be 600: owner read/write only)
    file_mode = file_stat.st_mode
    if (file_mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)) != 0:
        raise ValueError(
            f"Log file {path_to_logfile} has insecure permissions. "
            f"Expected 600 (u=rw), actual: {stat.filemode(file_mode)}. "
            f"Remove permissions for group and others."
        )

    # Ensure the file mode is explicitly 600
    if (file_mode & 0o777) != 0o600:
        try:
            path.chmod(0o600)
        except Exception as e:
            raise OSError(f"Failed to set secure permissions (600) on log file: {e}")

    # Append confidential data to the log file
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(confidential_data + "\n")
    except Exception as e:
        raise OSError(f"Failed to write to log file: {e}")