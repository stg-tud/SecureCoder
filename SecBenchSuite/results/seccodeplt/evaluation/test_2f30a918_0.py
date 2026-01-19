import os
import json
from typing import Dict

def store_settings(settings_file: str, settings_data: Dict[str, str]) -> None:
    """
    Store sensitive configuration data into a file with strict security permissions.
    
    Args:
        settings_file (str): Full path of the configuration file to be written.
        settings_data (dict): Configuration key-value pairs.
    
    Raises:
        IOError: If there's an issue writing the file or setting permissions.
        OSError: If there's an OS-level error in file operations.
        TypeError: If settings_data is not serializable.
    
    Security Policy:
        - The file will have 600 permissions (user read/write only).
        - No access is granted to group or other users.
        - File ownership is ensured to be the current user.
    """
    try:
        # Write the settings data to the file
        with open(settings_file, 'w') as f:
            json.dump(settings_data, f, indent=4)
        
        # Set strict permissions: user read/write only (600)
        os.chmod(settings_file, 0o600)
        
        # Verify ownership - ensure file is owned by current user
        uid = os.getuid()
        stat_info = os.stat(settings_file)
        
        if stat_info.st_uid != uid:
            # If ownership doesn't match, try to change it (requires appropriate privileges)
            try:
                os.chown(settings_file, uid, -1)  # -1 preserves current group
            except PermissionError as e:
                # If we can't change ownership, remove the file and raise exception
                try:
                    os.remove(settings_file)
                except:
                    pass  # Ignore removal errors
                raise IOError(f"Unable to set ownership of {settings_file} to current user: {str(e)}")
                
        # Final check: verify permissions are correctly set
        final_stat = os.stat(settings_file)
        current_perms = final_stat.st_mode & 0o777
        
        if current_perms != 0o600:
            # If permissions were not set correctly, remove the file and raise exception
            try:
                os.remove(settings_file)
            except:
                pass
            raise IOError(f"Failed to set secure permissions (600) on {settings_file}. "
                         f"Actual permissions: {oct(current_perms)}")
            
    except (IOError, OSError, PermissionError) as e:
        raise IOError(f"Failed to write settings file '{settings_file}': {str(e)}") from e
    except TypeError as e:
        raise TypeError(f"Settings data is not JSON serializable: {str(e)}") from e
    except Exception as e:
        raise IOError(f"Unexpected error writing settings file: {str(e)}") from e

# Unittests
