import os
import json
import fcntl

def change_config(cfg_path: str, new_cfg: dict) -> bool:
    """
    Updates the configuration file with new configuration data.
    
    Args:
        cfg_path (str): Path to the configuration file to update.
        new_cfg (dict): New configuration data to write.
    
    Returns:
        bool: True if update is successful, False otherwise.
    """
    # Check if file exists
    if not os.path.exists(cfg_path):
        return False
    
    try:
        # Open file in read-write mode
        with open(cfg_path, 'r+') as f:
            # Apply exclusive lock with timeout protection (non-blocking)
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                return False  # Another process holds the lock
            
            try:
                # Read current config (validate it's valid JSON)
                try:
                    config_data = json.load(f)
                    if not isinstance(config_data, dict):
                        config_data = {}
                except json.JSONDecodeError:
                    config_data = {}
                
                # Move to the beginning of the file and truncate
                f.seek(0)
                f.truncate()
                
                # Write the new configuration
                json.dump(new_cfg, f, indent=4)
                
                # Ensure data is written to disk
                f.flush()
                os.fsync(f.fileno())
                
            except (OSError, IOError, TypeError):
                # If writing fails, return False
                return False
            finally:
                # Release the lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return True
        
    except (OSError, IOError):
        return False