import os
import stat
import getpass

def write_protected_log(log_path: str, secret_info: str) -> None:
    """
    Writes sensitive information to a log file with strict permissions.
    
    Ensures the log file has permissions set to 600 (owner read/write only)
    and is owned by the current user before writing any sensitive data.
    
    Args:
        log_path: The absolute file path where the sensitive data needs to be logged.
        secret_info: The sensitive data (like passwords or tokens) that require logging.
        
    Raises:
        Exception: If there's any issue ensuring secure writing of sensitive information.
    """
    try:
        # Get current user
        current_user = getpass.getuser()
        
        # Check if file exists
        file_exists = os.path.exists(log_path)
        
        if file_exists:
            # Get file status
            file_stat = os.stat(log_path)
            
            # Check permissions - must be 600 (0o600)
            current_permissions = stat.S_IMODE(file_stat.st_mode)
            if current_permissions != 0o600:
                raise PermissionError(f"File permissions must be 600, but are {oct(current_permissions)}")
            
            # Check ownership
            file_owner = pwd.getpwuid(file_stat.st_uid).pw_name if 'pwd' in globals() else file_stat.st_uid
            if str(file_owner) != current_user:
                raise PermissionError(f"File must be owned by user '{current_user}', but is owned by '{file_owner}'")
        else:
            # File doesn't exist, will be created with secure permissions
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(log_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, mode=0o700, exist_ok=True)
        
        # Write the sensitive data to the file with secure permissions
        # Use open with mode 'a' to append and set permissions explicitly
        with os.fdopen(
            os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600),
            'a'
        ) as f:
            f.write(secret_info + '\n')
        
        # Double-check the file permissions after creation/writing
        final_stat = os.stat(log_path)
        final_permissions = stat.S_IMODE(final_stat.st_mode)
        if final_permissions != 0o600:
            raise Exception(f"Failed to maintain secure permissions on log file: {oct(final_permissions)}")
            
        # Verify ownership again
        final_owner = pwd.getpwuid(final_stat.st_uid).pw_name if 'pwd' in globals() else final_stat.st_uid
        if str(final_owner) != current_user:
            raise Exception(f"File ownership changed unexpectedly: now owned by '{final_owner}'")
            
    except Exception as e:
        raise Exception(f"Failed to securely write to log file: {str(e)}")

# Import pwd only if available (Unix-like systems)
try:
    import pwd
except ImportError:
    # pwd is not available on Windows, we'll handle this in the function
    pass