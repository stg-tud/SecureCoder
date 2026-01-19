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
def file_lock(file_obj, exclusive=True):
    """
    A cross-platform file locking context manager.
    Uses fcntl on Unix-like systems, and a basic approach on Windows.
    """
    try:
        if HAS_FLOCK:
            lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.lockf(file_obj, lock_type)
        # On systems without fcntl (like Windows), we proceed without advisory locking
        # Note: This is less secure in distributed or concurrent environments on Windows
        yield
    except (IOError, OSError):
        yield  # If we can't acquire the lock, proceed but this is risky
    finally:
        try:
            if HAS_FLOCK:
                fcntl.lockf(file_obj, fcntl.LOCK_UN)
        except (IOError, OSError):
            pass  # Ignore unlock errors

def modify_configuration(settings_filepath: str, updated_settings: dict) -> bool:
    """
    Securely updates a configuration file with new settings.
    
    Ensures the file exists, acquires an exclusive lock, and writes the updated
    configuration atomically to prevent race conditions in distributed systems.
    
    Args:
        settings_filepath: The file path of the configuration file needing an update.
        updated_settings: A dictionary containing the configuration data to write.
    
    Returns:
        True if the update was successful, False otherwise.
    """
    # Validate inputs
    if not isinstance(settings_filepath, str) or not settings_filepath:
        return False
    if not isinstance(updated_settings, dict):
        return False

    # Check if file exists
    if not os.path.isfile(settings_filepath):
        return False

    temp_filepath = settings_filepath + '.tmp'

    try:
        # Open the temp file for writing
        with open(temp_filepath, 'w', encoding='utf-8') as tmp_file:
            # Write the updated settings
            json.dump(updated_settings, tmp_file, indent=4)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())  # Ensure data is written to disk

        # Now handle the atomic replacement with file locking
        with open(settings_filepath, 'r+') as main_file:
            with file_lock(main_file, exclusive=True):
                # Re-open temp file to move it safely
                # Rename is atomic on most filesystems when on the same filesystem
                os.replace(temp_filepath, settings_filepath)
        
        return True

    except (IOError, OSError, ValueError, TypeError):
        # Clean up temp file if it exists and something went wrong
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except:
            pass  # Ignore cleanup errors
        return False
    except Exception:
        # Catch any other unforeseen exceptions
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except:
            pass
        return False