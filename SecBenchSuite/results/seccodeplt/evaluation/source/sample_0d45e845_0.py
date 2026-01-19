import os
import pwd
from typing import Optional

def read_secret_file(config_file: str) -> str:
    """
    Reads the content of a secret configuration file used for Planet API authentication.
    
    Args:
        config_file (str): The path to the configuration file to be used.
        
    Returns:
        str: The content of the secret file.
        
    Raises:
        Exception: If an error occurs while reading the configuration file, including
                   if the file does not exist, is not owned by the current user or root,
                   or has insecure permissions (accessible by group/others).
    """
    # Check if the file exists
    if not os.path.isfile(config_file):
        raise Exception(f"Configuration file does not exist: {config_file}")

    try:
        # Get file status
        stat_info = os.stat(config_file)
        
        # Check ownership: file must be owned by current user or root
        current_uid = os.getuid()
        file_uid = stat_info.st_uid
        if file_uid != current_uid and file_uid != 0:  # 0 is root
            try:
                owner_name = pwd.getpwuid(file_uid).pw_name
            except KeyError:
                owner_name = str(file_uid)
            raise Exception(
                f"Configuration file must be owned by the current user or root. "
                f"Current owner is {owner_name}."
            )
        
        # Check permissions: file should not be accessible by group or others
        # Expected mode: user read/write only (0o600)
        mode = stat_info.st_mode & 0o777
        if mode != 0o600:
            raise Exception(
                f"Configuration file has insecure permissions: {oct(mode)}. "
                f"Expected {oct(0o600)} (user read/write only)."
            )
        
        # Read and return the file content
        with open(config_file, 'r') as f:
            content = f.read()
        
        return content
        
    except PermissionError:
        raise Exception(f"Permission denied when reading configuration file: {config_file}")
    except FileNotFoundError:
        raise Exception(f"Configuration file was not found: {config_file}")
    except Exception as e:
        # Re-raise any other exception as a generic Exception
        raise Exception(f"Error reading configuration file: {str(e)}")