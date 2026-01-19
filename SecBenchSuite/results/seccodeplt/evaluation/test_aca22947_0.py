import os
import stat
from pathlib import Path

def log_confidential_data(log_path: str, sensitive_content: str) -> None:
    """
    Logs sensitive content to a file with strict security checks.

    Ensures the log file has secure permissions (600) and is owned by the current user.
    Raises an exception if security requirements are not met.

    Args:
        log_path (str): The path of the log file where the sensitive data will be appended.
        sensitive_content (str): The sensitive information (passwords, tokens, etc.) needing to be logged.

    Returns:
        None

    Raises:
        ValueError: If the file is not owned by the current user or permissions are too permissive.
        IOError: If there is an issue accessing or writing to the file.
        RuntimeError: If the current user cannot be determined.
    """
    log_path = Path(log_path)

    # Get current user's UID
    try:
        current_uid = os.getuid()
    except Exception as e:
        raise RuntimeError(f"Unable to determine current user ID: {e}")

    # Check if file exists
    if log_path.exists():
        # Verify ownership
        file_stat = log_path.stat()
        if file_stat.st_uid != current_uid:
            raise ValueError(
                f"Log file '{log_path}' is not owned by the current user. "
                f"Expected UID {current_uid}, but found UID {file_stat.st_uid}."
            )

        # Verify file permissions (must be 600: readable/writable only by owner)
        mode = file_stat.st_mode
        if (mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)) != 0:
            current_perms = stat.filemode(mode)
            raise ValueError(
                f"Log file '{log_path}' has insecure permissions: {current_perms}. "
                "Expected permissions: 600 (only user readable/writable)."
            )
    else:
        # Create the file with secure mode if it doesn't exist
        try:
            log_path.touch(mode=0o600, exist_ok=True)
            file_stat = log_path.stat()
            if file_stat.st_uid != current_uid:
                log_path.unlink()  # Clean up
                raise ValueError(
                    f"Created log file '{log_path}' is not owned by current user. "
                    f"Expected UID {current_uid}, got {file_stat.st_uid}."
                )
        except PermissionError as e:
            raise IOError(f"Permission denied when creating log file '{log_path}': {e}")
        except Exception as e:
            raise IOError(f"Failed to create log file '{log_path}': {e}")

    # Append sensitive content
    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(sensitive_content + "\n")
    except Exception as e:
        raise IOError(f"Failed to write sensitive data to '{log_path}': {e}")

# Unittests
