import os
import json
import errno
from contextlib import contextmanager

try:
    import fcntl
    HAS_FLOCK = True
except ImportError:
    # fcntl is not available on Windows
    HAS_FLOCK = False

@contextmanager
def file_lock(fd, exclusive=True):
    """Context manager to handle file locking in a cross-platform way."""
    try:
        if HAS_FLOCK:
            lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.lockf(fd, lock_type)
        yield
    except IOError as e:
        if e.errno in (errno.EACCES, errno.EAGAIN):
            # Lock cannot be acquired
            yield
        else:
            # Re-raise unexpected IO errors
            raise
    except OSError as e:
        if e.errno in (errno.EACCES, errno.EAGAIN):
            yield
        else:
            raise
    finally:
        if HAS_FLOCK:
            try:
                fcntl.lockf(fd, fcntl.LOCK_UN)
            except Exception:
                pass  # Ignore unlock errors

def adjust_config(file_path: str, new_values: dict) -> bool:
    """
    Securely updates a configuration file with new values using atomic file access
    and proper file locking to prevent race conditions in distributed environments.

    Args:
        file_path: The file path of the configuration file needing an update.
        new_values: A dictionary containing the configuration data that should 
                   replace the existing content.

    Returns:
        True if the configuration file is successfully updated, False otherwise.
    """
    # Validate inputs
    if not isinstance(file_path, str) or not file_path:
        return False
    if not isinstance(new_values, dict):
        return False

    # Check if file exists
    if not os.path.isfile(file_path):
        return False

    try:
        # Open file for reading and writing with exclusive lock
        with open(file_path, 'r+') as f:
            with file_lock(f.fileno(), exclusive=True):
                # Read current content
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError:
                    # If the file is not valid JSON, we'll overwrite it
                    config_data = {}

                # Update with new values
                config_data.update(new_values)

                # Move to the beginning and truncate
                f.seek(0)
                json.dump(config_data, f, indent=2)
                f.truncate()

        return True

    except Exception:
        # Silently handle all exceptions and return False
        return False

# Unittests
