import os
import json
import fcntl

def update_configuration(config_path: str, new_config: dict) -> bool:
    """
    Updates the configuration file with new configuration data.
    
    Args:
        config_path: str, the path to the configuration file to be updated.
        new_config: dict, containing the updated configuration data.
    
    Returns:
        bool: True if the configuration was successfully updated, 
              False if the file doesn't exist or the update failed.
    
    Security: Uses file locking to prevent race conditions during the 
              check-and-update operation in distributed environments.
    """
    # Check if file exists
    if not os.path.exists(config_path):
        return False
    
    try:
        # Open file in read-write mode
        with open(config_path, 'r+') as f:
            # Acquire exclusive lock (blocking)
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            
            try:
                # Read current configuration
                try:
                    current_config = json.load(f)
                except json.JSONDecodeError:
                    # If file is empty or invalid JSON, start with empty dict
                    current_config = {}
                
                # Update the configuration
                current_config.update(new_config)
                
                # Move file pointer to beginning and truncate
                f.seek(0)
                f.truncate()
                
                # Write updated configuration
                json.dump(current_config, f, indent=2)
                
                # Ensure data is written to disk
                f.flush()
                os.fsync(f.fileno())
                
                return True
                
            finally:
                # Always release the lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
    except (IOError, OSError, PermissionError, TypeError, ValueError):
        # Handle various potential errors (permissions, disk issues, etc.)
        return False

# Unittests
