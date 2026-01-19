import os
import stat
from pathlib import Path

def log_user_data(logfile_path: str, sensitive_info: str) -> None:
    """
    Securely logs sensitive user data to a specified file with restricted permissions.

    Args:
        logfile_path (str): Full file path where the sensitive data should be appended.
        sensitive_info (str): Confidential data such as passwords or tokens to log.

    Raises:
        ValueError: If logfile_path is empty or sensitive_info is empty.
        IOError: If there's an issue creating, accessing, or securing the log file.
        PermissionError: If the file cannot be secured due to permission constraints.
        OSError: If there's an OS-level error during file or permission operations.
    """
    if not logfile_path:
        raise ValueError("logfile_path must be a non-empty string.")
    if not sensitive_info:
        raise ValueError("sensitive_info must be a non-empty string.")

    log_path = Path(logfile_path)

    try:
        # Create parent directories if they don't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Open the file in append mode to add the sensitive info
        with log_path.open('a', encoding='utf-8') as f:
            f.write(sensitive_info + '\n')

        # Get current user's UID
        current_uid = os.getuid()

        # Ensure the file is owned by the current user
        file_stat = log_path.stat()
        if file_stat.st_uid != current_uid:
            # Attempt to change ownership to current user (may require appropriate privileges)
            try:
                os.chown(log_path, current_uid, -1)
            except PermissionError as e:
                raise PermissionError(f"Failed to set file owner to current user: {e}")

        # Enforce strict file permissions: 600 (owner read/write only)
        log_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

        # Final verification of ownership and permissions
        final_stat = log_path.stat()
        if final_stat.st_uid != current_uid:
            raise IOError(f"File {logfile_path} is not owned by the current user.")
        
        current_permissions = stat.S_IMODE(final_stat.st_mode)
        expected_permissions = stat.S_IRUSR | stat.S_IWUSR  # 600
        if current_permissions != expected_permissions:
            raise IOError(f"File permissions are {oct(current_permissions)}, expected {oct(expected_permissions)}.")

    except PermissionError as pe:
        raise PermissionError(f"Permission denied while handling log file: {pe}")
    except OSError as oe:
        raise IOError(f"OS error occurred while logging sensitive data: {oe}") from oe
    except Exception as e:
        raise IOError(f"Failed to securely log sensitive data: {e}") from e