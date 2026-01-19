import os
import shutil
import pwd
import getpass

def copy_files_securely(src_folder: str, dst_folder: str) -> None:
    """
    Transfers files from a source directory to a destination directory,
    but only if the destination directory is owned by the user running the script.
    
    Args:
        src_folder: Path to the directory containing files to be copied
        dst_folder: Path to the directory where files will be copied
    
    Returns:
        None
    
    Raises:
        PermissionError: If the destination directory is not owned by the current user
        FileNotFoundError: If source directory does not exist
        Exception: For other file operation errors
    """
    src_path = os.path.abspath(src_folder)
    dst_path = os.path.abspath(dst_folder)
    
    # Check if source directory exists
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source directory does not exist: {src_path}")
    
    if not os.path.isdir(src_path):
        raise NotADirectoryError(f"Source path is not a directory: {src_path}")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    
    # Verify destination is a directory
    if not os.path.isdir(dst_path):
        raise NotADirectoryError(f"Destination path is not a directory: {dst_path}")
    
    # Get current username
    current_user = getpass.getuser()
    
    # Check if destination directory is owned by current user
    try:
        dst_stat = os.stat(dst_path)
        dst_uid = dst_stat.st_uid
        
        # Get username from uid
        dst_owner = pwd.getpwuid(dst_uid).pw_name
        
        if dst_owner != current_user:
            raise PermissionError(
                f"Destination directory {dst_path} is owned by {dst_owner}, "
                f"not by current user {current_user}"
            )
    except KeyError:
        # This might happen if the uid doesn't have a corresponding entry in passwd
        raise PermissionError(f"Unable to verify ownership of destination directory: {dst_path}")
    
    # Copy files from source to destination
    try:
        for item in os.listdir(src_path):
            src_item = os.path.join(src_path, item)
            dst_item = os.path.join(dst_path, item)
            
            try:
                if os.path.isfile(src_item):
                    shutil.copy2(src_item, dst_item)  # copy2 preserves metadata
                elif os.path.isdir(src_item):
                    if os.path.exists(dst_item):
                        # If directory already exists, just copy contents
                        copy_files_securely(src_item, dst_item)
                    else:
                        shutil.copytree(src_item, dst_item)
            except PermissionError as e:
                print(f"Permission denied when copying {src_item}: {e}")
                continue
            except Exception as e:
                print(f"Error copying {src_item}: {e}")
                continue
                
    except PermissionError as e:
        raise PermissionError(f"Insufficient permissions to read source directory: {e}")
    except Exception as e:
        raise Exception(f"Error accessing source directory: {e}")