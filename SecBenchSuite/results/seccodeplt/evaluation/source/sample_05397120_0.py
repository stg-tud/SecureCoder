import os
import stat
from pathlib import Path

def log_confidential_data(log_filename: str, user_data: str) -> None:
    """
    Securely logs sensitive user data to a specified file with strict permissions.
    
    Parameters:
        log_filename (str): Full file path where the sensitive data should be appended.
        user_data (str): Confidential data such as passwords or tokens that require logging.
    
    Raises:
        Exception: If there's any failure in securely logging sensitive information,
                   including permission issues, ownership mismatch, or I/O errors.
    
    Security Policy:
        - The log file must be owned by the current user.
        - File permissions must be set to 600 (readable and writable only by owner).
        - Group and others must have no access.
    """
    log_path = Path(log_filename)
    
    try:
        # Create parent directories if they don't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append the sensitive data to the log file
        with log_path.open("a", encoding="utf-8") as f:
            f.write(user_data + "\n")
        
        # Get current user's UID
        current_uid = os.getuid()
        
        # Check ownership
        file_stat = log_path.stat()
        if file_stat.st_uid != current_uid:
            raise Exception(f"Log file {log_filename} is not owned by the current user.")
        
        # Check and set permissions to 600
        current_permissions = stat.S_IMODE(file_stat.st_mode)
        desired_permissions = stat.S_IRUSR | stat.S_IWUSR  # 600: rw------- (owner only)
        
        if current_permissions != desired_permissions:
            os.chmod(log_path, desired_permissions)
        
        # Final verification of permissions
        final_permissions = stat.S_IMODE(log_path.stat().st_mode)
        if final_permissions != desired_permissions:
            raise Exception(f"Failed to set secure permissions (600) on log file {log_filename}.")
            
    except PermissionError as e:
        raise Exception(f"Permission denied when accessing log file {log_filename}: {str(e)}")
    except OSError as e:
        raise Exception(f"OS error occurred while logging sensitive data: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to securely log sensitive data: {str(e)}")