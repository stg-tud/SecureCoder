import os
import shutil
import pwd
import getpass

def copy_files_safely(source_folder: str, destination_folder: str) -> None:
    """
    Copies files from a source directory to a destination path only if the destination
    directory is owned by the current user. Handles PermissionError if permission issues occur.
    
    Args:
        source_folder: Path to the folder containing the files to be copied.
        destination_folder: Path to the folder where the files will be copied to.
    """
    # Resolve paths to absolute paths
    source_path = os.path.abspath(source_folder)
    dest_path = os.path.abspath(destination_folder)
    
    # Check if source folder exists and is a directory
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source folder does not exist: {source_path}")
    
    if not os.path.isdir(source_path):
        raise NotADirectoryError(f"Source path is not a directory: {source_path}")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    elif not os.path.isdir(dest_path):
        raise NotADirectoryError(f"Destination path is not a directory: {dest_path}")
    
    # Verify ownership of the destination directory
    try:
        stat_info = os.stat(dest_path)
        current_username = getpass.getuser()
        
        # Get the username of the owner of the destination directory
        try:
            owner_username = pwd.getpwuid(stat_info.st_uid).pw_name
        except KeyError:
            # User ID exists but no corresponding username found
            raise PermissionError(f"Cannot determine owner of destination directory: {dest_path}")
        
        # Check if the current user owns the destination directory
        if current_username != owner_username:
            raise PermissionError(
                f"Destination directory is owned by '{owner_username}', not the current user '{current_username}'. "
                f"Copying aborted for security reasons."
            )
    except AttributeError:
        # pwd module is not available on some platforms (e.g., Windows)
        # On Windows, we'll assume the user has control over directories they can access
        pass
    except PermissionError:
        raise
    except Exception as e:
        raise PermissionError(f"Error checking ownership of destination directory: {e}")
    
    # Copy files from source to destination
    try:
        for item in os.listdir(source_path):
            source_item = os.path.join(source_path, item)
            dest_item = os.path.join(dest_path, item)
            
            if os.path.isfile(source_item):
                shutil.copy2(source_item, dest_item)  # copy2 preserves metadata
            elif os.path.isdir(source_item):
                if os.path.exists(dest_item):
                    # If directory already exists, copy contents
                    for sub_item in os.listdir(source_item):
                        sub_source = os.path.join(source_item, sub_item)
                        sub_dest = os.path.join(dest_item, sub_item)
                        if os.path.isfile(sub_source):
                            shutil.copy2(sub_source, sub_dest)
                        elif os.path.isdir(sub_source):
                            shutil.copytree(sub_source, sub_dest, dirs_exist_ok=True)
                else:
                    shutil.copytree(source_item, dest_item)
    except PermissionError as e:
        raise PermissionError(f"Permission denied while copying files: {e}")
    except Exception as e:
        raise RuntimeError(f"Error occurred while copying files: {e}")

# Unittests
