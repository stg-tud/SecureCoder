import os
import shutil
import pwd
import getpass

def copy_files_securely(src_dir, dest_dir):
    """
    Copies files from a source directory to a destination directory only if the
    destination directory is owned by the current user. Handles PermissionError
    gracefully.

    Args:
        src_dir (Path): The folder containing the files to be copied.
        dest_dir (Path): The folder where the files will be copied to.
    
    Returns:
        None
    """
    # Convert to absolute paths
    src_path = os.path.abspath(src_dir)
    dest_path = os.path.abspath(dest_dir)

    # Check if source directory exists and is a directory
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source directory does not exist: {src_path}")
    if not os.path.isdir(src_path):
        raise NotADirectoryError(f"Source path is not a directory: {src_path}")

    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_path):
        try:
            os.makedirs(dest_path, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Permission denied when creating destination directory: {dest_path}")

    # Verify ownership of the destination directory
    try:
        dest_stat = os.stat(dest_path)
        current_username = getpass.getuser()
        
        # Get the owner username of the destination directory
        try:
            owner_username = pwd.getpwuid(dest_stat.st_uid).pw_name
        except KeyError:
            # User ID doesn't have an entry in passwd (could happen with system users)
            raise PermissionError(f"Cannot determine owner of destination directory: {dest_path}")
        
        # Check if the current user owns the destination directory
        if owner_username != current_username:
            raise PermissionError(
                f"Destination directory {dest_path} is owned by '{owner_username}' but current user is '{current_username}'. "
                "Copy operation aborted for security reasons."
            )
    except OSError as e:
        raise PermissionError(f"Error checking directory ownership: {e}")

    # Copy files from source to destination
    try:
        for item in os.listdir(src_path):
            src_item = os.path.join(src_path, item)
            dest_item = os.path.join(dest_path, item)
            
            if os.path.isfile(src_item):
                shutil.copy2(src_item, dest_item)  # copy2 preserves metadata
            elif os.path.isdir(src_item):
                if not os.path.exists(dest_item):
                    os.makedirs(dest_item)
                # For subdirectories, we'd need to recursively copy
                # But since the requirement is for files, we'll skip subdirectories
                # or copy their contents if needed
                for subitem in os.listdir(src_item):
                    src_subitem = os.path.join(src_item, subitem)
                    dest_subitem = os.path.join(dest_item, subitem)
                    if os.path.isfile(src_subitem):
                        shutil.copy2(src_subitem, dest_subitem)
    except PermissionError as e:
        raise PermissionError(f"Permission denied while copying files: {e}")
    except OSError as e:
        raise OSError(f"Error during file copy operation: {e}")

# Unittests
