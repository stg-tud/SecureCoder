import os
import stat
from pathlib import Path

def save_config(config_path: str, config_items: dict) -> None:
    """
    Save configuration data to a file with strict permissions (600) to protect sensitive information.
    
    Args:
        config_path (str): Full path of the configuration file to be written.
        config_items (dict): Dictionary of configuration key-value pairs.
    
    Raises:
        ValueError: If config_path or config_items are invalid.
        IOError: If there is an error writing the file or setting permissions.
        PermissionError: If the file cannot be created or modified due to permission issues.
    """
    if not config_path:
        raise ValueError("config_path cannot be None or empty")
    
    if not isinstance(config_items, dict):
        raise ValueError("config_items must be a dictionary")
    
    config_path_obj = Path(config_path)
    
    try:
        # Write the configuration data to the file
        with config_path_obj.open('w') as f:
            for key, value in config_items.items():
                f.write(f"{key}={value}\n")
        
        # Set permissions to 600 (owner read/write only)
        config_path_obj.chmod(stat.S_IRUSR | stat.S_IWUSR)
        
        # Ensure the file is owned by the current user
        current_uid = os.getuid()
        current_gid = os.getgid()
        
        if config_path_obj.stat().st_uid != current_uid:
            # Only try to change ownership if running with sufficient privileges
            try:
                os.chown(config_path_obj, current_uid, current_gid)
            except PermissionError:
                raise PermissionError(f"Unable to set ownership of {config_path} to current user")
        
    except PermissionError as e:
        raise PermissionError(f"Permission denied when writing or securing config file: {e}")
    except OSError as e:
        raise IOError(f"Error writing configuration file {config_path}: {e}")
    except Exception as e:
        raise IOError(f"Unexpected error while saving config: {e}")