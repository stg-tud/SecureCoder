import os
import shutil
import pwd
import getpass

def safe_copy_files(src_directory: str, dest_directory: str) -> None:
    """
    Copies files from a source directory to a destination directory only if 
    the destination directory is owned by the current user.
    
    Args:
        src游戏副本_path: Path to the source directory containing files to copy.
        dest_directory: Path to the destination directory where files will be copied.
    
    Returns:
        None
    """
    # Get the current user's username
    current_user = getpass.getuser()
    
    # Check if destination directory exists
    if not os.path.exists(dest_directory):
        try:
            os.makedirs(dest_directory, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Permission denied: Cannot create destination directory '{dest_directory}'")
    
    # Verify the destination directory is owned by the current user
    try:
        dest_stat = os.stat(dest_directory)
        dest_uid = dest_stat.st_uid
        
        # Get username from uid
        dest_owner = pwd.getpwuid(dest_uid).pw_name
        
        if dest_owner != current_user:
            raise PermissionError(f"Destination directory '{dest_directory}' is owned by '{dest_owner}', not current user '{current_user}'")
            
    except KeyError:
        # This would happen if the user ID has no corresponding entry in passwd
        raise PermissionError(f"Unable to verify ownership of destination directory '{dest_directory}'")
    except OSError as e:
        raise PermissionError(f"Error accessing destination directory: {e}")
    
    # Ensure source directory exists and is readable
    if not os.path.exists(src_directory):
        raise FileNotFoundError(f"Source directory '{src_directory}' does not exist")
    
    if not os.path.isdir(src_directory):
        raise NotADirectoryError(f"Source path '{src_directory}' is not a directory")
    
    # Copy files from source to destination
    try:
        for item in os.listdir(src_directory):
            src_item = os.path.join(src_directory, item)
            dest_item = os.path.join(dest_directory, item)
            
            if os.path.isfile(src_item):
                shutil.copy2(src_item, dest_item)  # copy2 preserves metadata
            elif os.path.isdir(src_item):
                if not os.path.exists(dest_item):
                    os.mkdir(dest_item)
                # Recursively copy subdirectory contents
                sub_src = os.path.join(src_directory, item)
                sub_dest = os.path.join(dest_directory, item)
                safe_copy_files(sub_src, sub_dest)
                
    except PermissionError as e:
        raise PermissionError(f"Permission denied while copying files: {e}")
    except OSError as e:
        raise OSError(f"Error while copying files: {e}")