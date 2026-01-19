import os
import shutil
import pwd
import getpass

def safe_file_transfer(src_directory, dest_directory):
    """
    Transfers files from a given source directory to a destination directory,
    but only if the destination directory is owned by the user running the script.
    
    Args:
        src_directory: Path, directory containing files to be copied.
        dest_directory: Path, the directory where the files will be copied.
    
    Returns:
        None
    
    Raises:
        PermissionError: If the destination directory is not owned by the current user
                        or if copying fails due to insufficient permissions.
        FileNotFoundError: If source directory does not exist or is not accessible.
        NotADirectoryError: If the provided paths are not directories.
    """
    # Convert to Path objects if they aren't already
    src_path = os.fspath(src_directory)
    dest_path = os.fspath(dest_directory)
    
    # Check if source directory exists and is a directory
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source directory does not exist: {src_path}")
    
    if not os.path.isdir(src_path):
        raise NotADirectoryError(f"Source path is not a directory: {src_path}")
    
    # Check if destination directory exists and is a directory
    if not os.path.exists(dest_path):
        raise FileNotFoundError(f"Destination directory does not exist: {dest_path}")
    
    if not os.path.isdir(dest_path):
        raise NotADirectoryError(f"Destination path is not a directory: {dest_path}")
    
    # Get the current user's username
    current_user = getpass.getuser()
    
    # Get the owner of the destination directory
    try:
        dest_stat = os.stat(dest_path)
        try:
            # Try to get the username from the UID
            dest_owner = pwd.getpwuid(dest_stat.st_uid).pw_name
        except KeyError:
            # If the user doesn't exist in the password database
            raise PermissionError(f"Cannot determine owner of destination directory: {dest_path}")
            
    except OSError as e:
        raise PermissionError(f"Cannot access destination directory metadata: {e}")
    
    # Verify that the current user owns the destination directory
    if dest_owner != current_user:
        raise PermissionError(
            f"Destination directory {dest_path} is owned by {dest_owner}, "
            f"but current user is {current_user}. Transfer aborted for security reasons."
        )
    
    # Copy files from source to destination
    try:
        # Get list of files in the source directory
        for item in os.listdir(src_path):
            src_item = os.path.join(src_path, item)
            dest_item = os.path.join(dest_path, item)
            
            if os.path.isfile(src_item):
                try:
                    shutil.copy2(src_item, dest_item)  # copy2 preserves metadata
                except PermissionError as e:
                    print(f"Permission denied when copying {src_item} to {dest_item}: {e}")
                    continue
                except Exception as e:
                    print(f"Error copying {src_item} to {dest_item}: {e}")
                    continue
            elif os.path.isdir(src_item):
                # If it's a directory, you might want to copy it as well
                if not os.path.exists(dest_item):
                    try:
                        shutil.copytree(src_item, dest_item)
                    except PermissionError as e:
                        print(f"Permission denied when copying directory {src_item} to {dest_item}: {e}")
                        continue
                    except Exception as e:
                        print(f"Error copying directory {src_item} to {dest_item}: {e}")
                        continue
    
    except PermissionError as e:
        raise PermissionError(f"Insufficient permissions to read source directory: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during file transfer: {e}")