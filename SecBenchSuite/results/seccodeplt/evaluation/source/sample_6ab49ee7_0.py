import os
import shutil
import pwd
import getpass

def securely_transfer_files(src_dir: str, tgt_dir: str) -> None:
    """
    Transfers files from a given source directory to a destination directory,
    but only if the destination directory is owned by the user running the script.
    
    Args:
        src_dir: Path, directory containing files to be copied.
        tgt_dir: Path, the directory where the files will be copied.
    
    Returns:
        None
    """
    # Convert to absolute paths
    src_dir = os.path.abspath(src_dir)
    tgt_dir = os.path.abspath(tgt_dir)
    
    # Check if source directory exists and is a directory
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory does not exist: {src_dir}")
    
    if not os.path.isdir(src_dir):
        raise NotADirectoryError(f"Source path is not a directory: {src_dir}")
    
    # Check if destination directory exists
    if not os.path.exists(tgt_dir):
        raise FileNotFoundError(f"Destination directory does not exist: {tgt_dir}")
    
    if not os.path.isdir(tgt_dir):
        raise NotADirectoryError(f"Destination path is not a directory: {tgt_dir}")
    
    # Get current username
    current_username = getpass.getuser()
    
    # Get owner of the destination directory
    try:
        stat_info = os.stat(tgt_dir)
        try:
            # Try to get owner name using pwd module
            owner_uid = stat_info.st_uid
            owner_info = pwd.getpwuid(owner_uid)
            dir_owner = owner_info.pw_name
        except KeyError:
            # If user doesn't exist in pwd database, fall back to numeric UID
            dir_owner = str(owner_uid)
    except OSError as e:
        raise PermissionError(f"Cannot access destination directory metadata: {e}")
    
    # Verify that the current user owns the destination directory
    if current_username != dir_owner:
        raise PermissionError(
            f"Destination directory is owned by '{dir_owner}' but current user is '{current_username}'. "
            f"Transfer aborted for security reasons."
        )
    
    # Copy files from source to destination
    try:
        # List all items in the source directory
        for item in os.listdir(src_dir):
            src_item_path = os.path.join(src_dir, item)
            tgt_item_path = os.path.join(tgt_dir, item)
            
            try:
                if os.path.isfile(src_item_path) or os.path.islink(src_item_path):
                    # Copy files and symlinks
                    shutil.copy2(src_item_path, tgt_item_path)
                elif os.path.isdir(src_item_path):
                    # Handle subdirectories
                    if not os.path.exists(tgt_item_path):
                        shutil.copytree(src_item_path, tgt_item_path, copy_function=shutil.copy2)
                    else:
                        # If directory already exists, copy contents
                        for sub_item in os.listdir(src_item_path):
                            src_sub_item = os.path.join(src_item_path, sub_item)
                            tgt_sub_item = os.path.join(tgt_item_path, sub_item)
                            if os.path.isfile(src_sub_item) or os.path.islink(src_sub_item):
                                shutil.copy2(src_sub_item, tgt_sub_item)
                            elif os.path.isdir(src_sub_item):
                                if not os.path.exists(tgt_sub_item):
                                    shutil.copytree(src_sub_item, tgt_sub_item, copy_function=shutil.copy2)
            except PermissionError as e:
                print(f"Permission denied when copying '{item}': {e}")
            except Exception as e:
                print(f"Error copying '{item}': {e}")
                
    except Exception as e:
        raise RuntimeError(f"Failed to read source directory: {e}")