import os
import stat
import logging
from getpass import getuser
from pathlib import Path

def log_sensitive_data(log_file: str, sensitive_data: str) -> None:
    """
    Securely logs sensitive data to a file with strict permissions (600).
    
    Args:
        log_file (str): The full path to the log file.
        sensitive_data (str): The actual sensitive data to be logged for debugging purposes.
        
    Raises:
        ValueError: If log_file or sensitive_data is invalid.
        PermissionError: If unable to set proper file permissions.
        OSError: If there is an issue writing to the file or setting ownership/permissions.
        RuntimeError: If the file owner does not match the expected user.
    """
    if not log_file:
        raise ValueError("log_file path cannot be empty or None")
    
    if sensitive_data is None:
        raise ValueError("sensitive_data cannot be None")
    
    log_path = Path(log_file)
    
    try:
        # Ensure parent directories exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the sensitive data securely
        with log_path.open('a', encoding='utf-8') as f:
            f.write(f"{sensitive_data}\n")
        
        # Set permissions to 600 (owner read/write only)
        log_path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
        
        # Verify file permissions
        current_permissions = log_path.stat().st_mode & 0o777
        if current_permissions != 0o600:
            raise PermissionError(f"Failed to set secure permissions on {log_file}. Expected 600, got {oct(current_permissions)}")
        
        # Note: Actual ownership change (chown) requires root and is not done here.
        # We verify that the current user owns the file if possible.
        current_uid = os.getuid()
        file_uid = log_path.stat().st_uid
        
        if file_uid != current_uid:
            try:
                # On most systems, non-root users can't change ownership, but we alert if mismatched
                current_username = getuser()
                file_owner = Path(f'/home/{current_username}').expanduser().resolve() if current_username else None
                if file_owner and file_uid == file_owner.stat().st_uid:
                    pass  # Acceptable in some configurations
                else:
                    raise RuntimeError(f"Log file {log_file} is not owned by the current user (UID: {current_uid}). Owned by UID: {file_uid}")
            except (KeyError, FileNotFoundError):
                # getuser() might fail on some systems
                pass
        
    except PermissionError as e:
        raise PermissionError(f"Permission denied when securing log file {log_file}: {e}") from e
    except OSError as e:
        raise OSError(f"OS error occurred while logging sensitive data to {log_file}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while logging sensitive data: {e}") from e

# Unittests
