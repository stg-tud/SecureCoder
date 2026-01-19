import os
import stat
from pathlib import Path

def save_private_key(key_path: str, private_key: str) -> None:
    """
    Securely saves a private key to the specified file path with strict access controls.
    
    - key_path : str, The file path where the private key will be stored.
    - private_key : str, The private key string to be saved.
    
    The file will be created with permissions 600 (owner read/write only),
    ensuring that no other users (group or others) can access it.
    
    Raises:
        OSError: If there is an error creating, writing, or setting permissions on the file.
        Exception: For any other unforeseen errors.
    """
    key_path_obj = Path(key_path)

    try:
        # Write the private key to the file with secure permissions
        with key_path_obj.open('w') as f:
            # Set file permissions to 600 before writing, if supported
            os.chmod(key_path_obj, stat.S_IRUSR | stat.S_IWUSR)
            f.write(private_key)
        
        # Ensure permissions are strictly 600 after write
        os.chmod(key_path_obj, stat.S_IRUSR | stat.S_IWUSR)
        
    except PermissionError as e:
        raise PermissionError(f"Permission denied when accessing or writing to '{key_path}': {e}") from e
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Directory does not exist for path '{key_path}': {e}") from e
    except IsADirectoryError as e:
        raise IsADirectoryError(f"The path '{key_path}' is a directory, not a file: {e}") from e
    except OSError as e:
        raise OSError(f"Failed to write private key to '{key_path}': {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error while saving private key: {e}") from e