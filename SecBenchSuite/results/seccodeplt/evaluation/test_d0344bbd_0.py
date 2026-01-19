import os
import stat
import getpass

def secure_log_write(log_file_path: str, confidential_info: str) -> None:
    """
    Securely writes sensitive data to a log file with strict permissions and ownership checks.
    
    Args:
        log_file_path (str): The absolute file path where the sensitive data needs to be logged.
        confidential_info (str): The sensitive data (like passwords or tokens) that require logging.
    
    Raises:
        Exception: If there's any issue ensuring the secure writing of sensitive information.
    """
    if not log_file_path:
        raise Exception("Log file path cannot be empty or None.")
    
    if not os.path.isabs(log_file_path):
        raise Exception("Log file path must be an absolute path.")
    
    # Get current user
    current_username = getpass.getuser()
    
    try:
        # Check if file exists
        if os.path.exists(log_file_path):
            # Verify file ownership
            file_stat = os.stat(log_file_path)
            file_owner = file_stat.st_uid
            current_uid = os.getuid()
            
            if file_owner != current_uid:
                raise Exception(f"File {log_file_path} is not owned by the current user.")
            
            # Verify file permissions (must be 600 - readable/writable by owner only)
            file_mode = file_stat.st_mode
            if (file_mode & stat.S_IRWXG) != 0 or (file_mode & stat.S_IRWXO) != 0:
                raise Exception(f"File {log_file_path} has insecure permissions. Must be 600.")
        else:
            # File doesn't exist, create it with secure permissions
            # Create any necessary directories
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, mode=0o700, exist_ok=True)
    
        # Write the confidential information to the file with secure permissions
        # Using open with mode 'a' to append and setting permissions explicitly
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"{confidential_info}\n")
        
        # Ensure the file has correct permissions (600)
        os.chmod(log_file_path, stat.S_IRUSR | stat.S_IWUSR)
        
        # Verify ownership again after potential creation
        file_stat = os.stat(log_file_path)
        if file_stat.st_uid != os.getuid():
            raise Exception(f"Ownership verification failed for {log_file_path}.")
            
    except PermissionError as e:
        raise Exception(f"Permission denied when accessing {log_file_path}: {e}")
    except OSError as e:
        raise Exception(f"OS error occurred while handling the log file: {e}")
    except Exception as e:
        raise Exception(f"Failed to securely write to log file: {e}")

# Unittests
