import os
import json
import fcntl

def modify_config_file(config_file_path: str, latest_config: dict) -> bool:
    """
    Updates the configuration file with the provided latest configuration.
    
    This function checks if the file exists, acquires an exclusive lock to prevent
    race conditions in distributed environments, writes the updated configuration
    in JSON format, and ensures the file is properly synced to disk.
    
    Args:
        config_file_path (str): Path to the configuration file to update.
        latest_config (dict): New configuration data to write.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    # Check if the file exists
    if not os.path.exists(config_file_path):
        return False
    
    try:
        # Open file in read-write mode
        with open(config_file_path, 'r+') as f:
            # Acquire exclusive lock with non-blocking behavior
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            try:
                # Write the updated configuration
                f.seek(0)
                json.dump(latest_config, f, indent=4)
                f.truncate()  # Remove any leftover data if new content is shorter
                
                # Ensure data is written to disk
                f.flush()
                os.fsync(f.fileno())
            finally:
                # Release the lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
        return True
        
    except (IOError, OSError, ValueError, TypeError):
        # Handle any file I/O, locking, or JSON serialization errors
        return False

# Unittests
