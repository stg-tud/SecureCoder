import os
import json
import fcntl

def refresh_config_file(cfg_path: str, new_configuration: dict) -> bool:
    """
    Updates the configuration file with new configuration data.
    Ensures the file exists and uses file locking to prevent race conditions.
    
    Args:
        cfg_path (str): Path to the configuration file.
        new_configuration (dict): New configuration data to write.
    
    Returns:
        bool: True if update is successful, False otherwise.
    """
    # Check if the file exists
    if not os.path.exists(cfg_path):
        return False
    
    try:
        # Open the file in read-write mode
        with open(cfg_path, 'r+', encoding='utf-8') as f:
            # Acquire exclusive lock before writing
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            
            try:
                # Write the new configuration as JSON
                f.seek(0)
                json.dump(new_configuration, f, indent=4)
                f.truncate()  # In case the new content is shorter
                return True
            finally:
                # Always release the lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
    except (OSError, IOError, ValueError, TypeError):
        # Handle file I/O errors, encoding issues, or invalid JSON
        return False

# Unittests
