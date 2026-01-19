import os
import shutil
import getpass

def copy_files_safely(from_directory, to_directory):
    """
    Copies files from a specified source directory to a target directory,
    only if the target directory is owned by the running user.
    
    Args:
        from_directory (Path): Directory containing the files to be copied.
        to_directory (Path): Location where files are to be copied.
    
    Returns:
        None
    """
    # Convert to absolute paths
    from_dir = os.path.abspath(from_directory)
    to_dir = os.path.abspath(to_directory)
    
    # Check if source directory exists
    if not os.path.exists(from_dir):
        raise FileNotFoundError(f"Source directory does not exist: {from_dir}")
    
    if not os.path.isdir(from_dir):
        raise NotADirectoryError(f"Source path is not a directory: {from_dir}")
    
    # Check if target directory exists
    if not os.path.exists(to_dir):
        raise FileNotFoundError(f"Target directory does not exist: {to_dir}")
    
    if not os.path.isdir(to_dir):
        raise NotADirectoryError(f"Target path is not a directory: {to_dir}")
    
    # Get current user
    current_user = getpass.getuser()
    
    # Get owner of target directory
    try:
        stat_info = os.stat(to_dir)
        # On Unix-like systems, we need to get username from uid
        try:
            import pwd
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
        except (ImportError, KeyError):
            # Fallback for systems where pwd is not available (e.g., Windows)
            owner = stat_info.st_uid
            # On Windows, compare with current user directly
            if os.name == 'nt':
                owner = current_user
    except OSError as e:
        raise PermissionError(f"Cannot access directory metadata: {e}")
    
    # On Windows, we can't reliably get file ownership via st_uid,
    # so we'll assume we have ownership if we can write to the directory
    if os.name == 'nt':
        # For Windows, check if we can write to the directory instead
        if not os.access(to_dir, os.W_OK):
            raise PermissionError(f"Cannot write to target directory: {to_dir}")
    else:
        # For Unix-like systems, check ownership
        if str(owner) != current_user:
            raise PermissionError(f"Target directory is not owned by current user. Owner: {owner}, Current user: {current_user}")
    
    # Copy files from source to target directory
    try:
        # Iterate through all items in the source directory
        for item in os.listdir(from_dir):
            source_path = os.path.join(from_dir, item)
            target_path = os.path.join(to_dir, item)
            
            try:
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, target_path)  # copy2 preserves metadata
                elif os.path.isdir(source_path):
                    # If destination directory already exists, remove it first
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
            except PermissionError as e:
                print(f"Permission denied when copying {item}: {e}")
                continue
            except Exception as e:
                print(f"Error copying {item}: {e}")
                continue
                
    except PermissionError as e:
        raise PermissionError(f"Permission denied when accessing source directory: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during file copy: {e}")

# Unittests
