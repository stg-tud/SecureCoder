import os
import json
from typing import Dict

def modify_config(path_to_config: str, updated_config: Dict) -> bool:
    """
    Updates the configuration file with new data if the file exists.
    Uses file locking to prevent race conditions in a distributed environment.

    Args:
        path_to_config: Path to the configuration file.
        updated_config: Dictionary containing the new configuration data.

    Returns:
        True if update is successful, False otherwise.
    """
    # Check if the file exists
    if not os.path.exists(path_to_config):
        return False

    # Use file locking via opening in exclusive mode to prevent race conditions
    try:
        # Open the file in read-write mode
        with open(path_to_config, 'r+', encoding='utf-8') as f:
            try:
                # Lock the file for exclusive access (advisory lock)
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

                # Write the updated config
                f.seek(0)  # Move to the beginning
                json.dump(updated_config, f, indent=4)
                f.truncate()  # Remove any leftover data if new content is shorter

                # Flush and sync to disk
                f.flush()
                os.fsync(f.fileno())

                # Unlock is automatic when file is closed
                return True

            except (IOError, OSError, ValueError):
                return False
            finally:
                try:
                    if 'fcntl' in globals():
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except:
                    pass  # Best-effort unlock
    except (PermissionError, FileNotFoundError, OSError, BlockingIOError):
        # File disappeared or locked by another process
        return False
    except Exception:
        return False

    return False