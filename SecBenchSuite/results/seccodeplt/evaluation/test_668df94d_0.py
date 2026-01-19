import os
import stat
from pathlib import Path

def store_confidential_data(logging_file: str, confidential_data: str) -> None:
    """
    Securely logs confidential data to a file with strict permissions and ownership checks.
    
    Args:
        logging_file (str): The absolute file path where the sensitive data needs to be logged.
        confidential_data (str): The sensitive data (like passwords or tokens) that require logging.
    
    Raises:
        Exception: If there's any issue ensuring the secure writing of sensitive information.
    """
    try:
        logging_path = Path(logging_file)
        
        # Ensure the directory exists
        logging_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the data temporarily or update the file
        with open(logging_path, 'a') as f:
            f.write(confidential_data + '\n')
        
        # Set strict permissions: owner read/write only (600)
        logging_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        
        # Verify ownership - ensure the file is owned by the current user
        current_uid = os.getuid()
        file_stat = logging_path.stat()
        
        if file_stat.st_uid != current_uid:
            # If the file is not owned by the current user, raise an exception
            raise Exception(f"File {logging_file} is not owned by the current user. "
                            f"Expected UID: {current_uid}, Found UID: {file_stat.st_uid}")
        
        # Final permission check
        current_permissions = file_stat.st_mode & 0o777
        if current_permissions != 0o600:
            raise Exception(f"File {logging_file} does not have secure permissions. "
                            f"Expected 600, got {oct(current_permissions)}")
                            
    except Exception as e:
        raise Exception(f"Failed to securely log confidential data: {str(e)}")

# Unittests
