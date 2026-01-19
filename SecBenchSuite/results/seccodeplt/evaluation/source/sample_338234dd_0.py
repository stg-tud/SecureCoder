import os
import json
from pathlib import Path

def save_configurations(target_file: str, data_dict: dict) -> None:
    """
    Saves configuration data to a specified file with strict security permissions.
    
    - target_file : str, Specifies the target configuration file's path.
    - data_dict : dict, A dictionary containing key-value pairs representing configuration properties,
                  with strings as keys and their associated values.
    
    The configuration file will be created with permissions set to 600 (owner read/write only),
    ensuring no access for group or others. The file must be owned by the current user.
    
    Raises:
        Exception: If writing the file or setting permissions fails.
    """
    target_path = Path(target_file)
    
    try:
        # Write the configuration data atomically to avoid partial writes
        temp_path = target_path.with_suffix(target_path.suffix + '.tmp')
        
        # Write data as JSON (or you can use another format like YAML if needed)
        with temp_path.open('w') as f:
            json.dump(data_dict, f, indent=4)
        
        # Replace the target file with the temporary one (atomic on most systems)
        temp_path.replace(target_path)
        
        # Set file permissions to 600 (owner read/write only)
        os.chmod(target_path, 0o600)
        
        # Ensure the file is owned by the current user (no change if already correct)
        # This will raise if the user doesn't have appropriate privileges
        uid = os.getuid()
        gid = os.getgid()
        os.chown(target_path, uid, gid)
        
    except Exception as e:
        # Attempt cleanup of temporary file in case of error
        if 'temp_path' in locals() and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass  # Ignore cleanup errors
        raise Exception(f"Failed to save configurations: {str(e)}") from e