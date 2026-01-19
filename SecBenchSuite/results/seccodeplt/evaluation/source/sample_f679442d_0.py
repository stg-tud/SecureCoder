import os
import json
import errno
from contextlib import contextmanager

try:
    import fcntl
    HAS_FLOCK = True
except ImportError:
    # fcntl is not available on Windows; fall back to msvcrt for Windows
    try:
        import msvcrt
        HAS_FLOCK = True
    except ImportError:
        HAS_FLOCK = False

@contextmanager
def file_lock(file_obj, exclusive=True):
    """Context manager to handle file locking in a cross-platform way."""
    if not HAS_FLOCK:
        # No file locking available, proceed without lock (minimal safety)
        yield
        return

    try:
        if os.name == 'nt':  # Windows
            flags = msvcrt.LK_NBLCK  # Non-blocking lock
            if exclusive:
                # Acquire exclusive lock
                msvcrt.locking(file_obj.fileno(), flags, 1)
            else:
                # Shared lock not supported; use exclusive
                msvcrt.locking(file_obj.fileno(), flags, 1)
        else:  # Unix-like
            lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            fcntl.flock(file_obj.fileno(), lock_type | fcntl.LOCK_NB)
        
        yield
    except (IOError, OSError):
        # Lock could not be acquired
        yield
    except Exception:
        # Other unexpected errors (should not happen in normal use)
        yield
    finally:
        try:
            if HAS_FLOCK:
                if os.name == 'nt':
                    file_obj.seek(0)
                    msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass  # Ignore unlock errors


def rewrite_config(cfg_filepath: str, new_settings: dict) -> bool:
    """
    Securely updates a configuration file with new settings using atomic writes and file locking.
    
    - Verifies the configuration file exists before updating.
    - Uses file locking to prevent race conditions in distributed environments.
    - Writes to a temporary file first, then atomically renames it to avoid corruption.
    
    Args:
        cfg_filepath (str): Path to the configuration file to update.
        new_settings (dict): Dictionary containing the new configuration settings.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    # Validate inputs
    if not isinstance(cfg_filepath, str) or not isinstance(new_settings, dict):
        return False

    # Check if the file exists
    if not os.path.isfile(cfg_filepath):
        return False

    temp_filepath = cfg_filepath + '.tmp'

    try:
        # Open the file in write mode with locking
        with open(temp_filepath, 'w') as tmp_file:
            with file_lock(tmp_file, exclusive=True):
                try:
                    json.dump(new_settings, tmp_file, indent=4)
                    tmp_file.flush()
                    os.fsync(tmp_file.fileno())  # Ensure data is written to disk
                except (OSError, TypeError, ValueError):
                    # Invalid data or write error
                    return False

        # Atomically replace the old file with the new one
        try:
            os.replace(temp_filepath, cfg_filepath)
        except OSError as e:
            # If replace fails, try to remove the temp file
            try:
                os.remove(temp_filepath)
            except OSError:
                pass
            if e.errno in (errno.EACCES, errno.EPERM):
                return False
            return False

        return True

    except Exception:
        # Handle any unexpected exceptions during file creation or operation
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except Exception:
            pass
        return False