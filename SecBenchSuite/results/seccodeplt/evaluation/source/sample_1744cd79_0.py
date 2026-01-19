import os
import shutil
import pwd
import getpass

def safe_copy_files(src_directory: str, dest_directory: str) -> None:
    """
    Copy files from source directory to destination directory only if the 
    destination directory is owned by the current user.
    
    Args:
        src_directory: Path to the directory containing the files to be copied.
        dest_directory: Path to the location where files are to be copied.
    
    Returns:
        None
    """
    # Resolve paths to absolute paths
    src_path = os.path.abspath(src_directory)
    dest_path = os.path.abspath(dest_directory)
    
    # Check if source directory exists and is a directory
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source directory does not exist: {src_path}")
    
    if not os.path.isdir(src_path):
        raise NotADirectoryError(f"Source path is not a directory: {src_path}")
    
    # Check if destination directory exists
    if not os.path.exists(dest_path):
        raise FileNotFoundError(f"Destination directory does not exist: {dest_path}")
    
    if not os.path.isdir(dest_path):
        raise NotADirectoryError(f"Destination path is not a directory: {dest_path}")
    
    # Get current username
    current_user = getpass.getuser()
    
    # Get owner of destination directory
    try:
        dest_stat = os.stat(dest_path)
        dest_owner_uid = dest_stat.st_uid
        
        # Get username from UID
        dest_owner_name = pwd.getpwuid(dest_owner_uid).pw_name
        
        # Check if destination directory is owned by current user
        if dest_owner_name != current_user:
            print(f"Permission denied: Destination directory '{dest_path}' is not owned by current user '{current_user}'")
            return
            
    except (KeyError, PermissionError) as e:
        print(f"Unable to verify ownership of destination directory: {e}")
        return
    except Exception as e:
        print(f"Unexpected error checking directory ownership: {e}")
        return
    
    # Copy files from source to destination
    try:
        # Iterate through all items in the source directory
        for item in os.listdir(src_path):
            src_item_path = os.path.join(src_path, item)
            dest_item_path = os.path.join(dest_path, item)
            
            if os.path.isfile(src_item_path):
                # Copy individual files
                shutil.copy2(src_item_path, dest_item_path)
            elif os.path.isdir(src_item_path):
                # If it's a directory, copy the entire directory
                if os.path.exists(dest_item_path):
                    shutil.rmtree(dest_item_path)
                shutil.copytree(src_item_path, dest_item_path)
                
    except PermissionError as e:
        print(f"Permission denied while copying files: {e}")
    except Exception as e:
        print(f"Error occurred while copying files: {e}")