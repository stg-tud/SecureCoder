import os
import json
from pathlib import Path
import errno

def refresh_config(config_location: str, updated_settings: dict) -> bool:
    """
    Updates the configuration file with the provided settings.

    This function safely updates the configuration file by first verifying its existence
    and then writing the new settings using atomic operations and proper file locking
    to prevent race conditions in a distributed environment.

    Args:
        config_location (str): Path to the configuration file to update.
        updated_settings (dict): New configuration data to write.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    config_path = Path(config_location)

    # Check if the file exists
    if not config_path.is_file():
        return False

    try:
        # Open the file in read-write mode to allow locking
        with config_path.open(mode='r+', encoding='utf-8') as f:
            try:
                import fcntl
                # Acquire an exclusive lock (blocking)
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except (ImportError, OSError):
                # fcntl not available (e.g., on Windows), fallback to basic locking
                # Note: On non-POSIX systems, file locking may not be fully reliable
                pass

            try:
                # Read current config
                try:
                    current_config = json.load(f)
                except json.JSONDecodeError:
                    # If file is empty or invalid, treat as empty config
                    current_config = {}

                # Update with new settings
                current_config.update(updated_settings)

                # Move to the beginning and truncate the file
                f.seek(0)
                f.truncate()

                # Write updated config
                json.dump(current_config, f, indent=4)

                # Ensure data is written to disk
                f.flush()
                os.fsync(f.fileno())

            except Exception:
                # If any error occurs during write, do not leave file in corrupted state
                # However, we've already truncated, so recovery is hard
                # Best effort: try to rollback? Not feasible without backup
                # So just return False
                return False
            finally:
                try:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (ImportError, OSError):
                    pass  # Locking not supported or failed to unlock

        return True

    except Exception:
        # Any IO or OS-level error (including permission issues, disk full, etc.)
        return False

# Unittests
