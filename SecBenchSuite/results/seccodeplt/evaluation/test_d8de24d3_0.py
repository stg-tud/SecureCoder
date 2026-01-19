import os
import shutil
import getpass

def validated_copy_files(directory_from, directory_to):
    """
    Copies files from a specified source directory to a target directory,
    but only if the target directory is owned by the running user.
    
    Args:
        directory_from: Path, directory containing the files to be copied.
        directory_to: Path, location where files are to be copied.
    
    Returns:
        None
    """
    # Convert to absolute paths
    directory_from = os.path.abspath(directory_from)
    directory_to = os.path.abspath(directory_to)
    
    # Check if source directory exists and is a directory
    if not os.path.exists(directory_from):
        raise FileNotFoundError(f"Source directory does not exist: {directory_from}")
    
    if not os.path.isdir(directory_from):
        raise NotADirectoryError(f"Source path is not a directory: {directory_from}")
    
    # Check if target directory exists
    if not os.path.exists(directory_to):
        raise FileNotFoundError(f"Target directory does not exist: {directory_to}")
    
    if not os.path.isdir(directory_to):
        raise NotADirectoryError(f"Target path is not a directory: {directory_to}")
    
    # Get current user
    current_user = getpass.getuser()
    
    # Get owner of target directory
    try:
        stat_info = os.stat(directory_to)
        # On Unix-like systems, use pwd to get username from uid
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
        raise PermissionError(f"Cannot access directory information for {directory_to}: {e}")
    
    # Check if current user owns the target directory
    if owner != current_user:
        raise PermissionError(f"Target directory {directory_to} is not owned by current user ({current_user})")
    
    # Copy files from source to target
    try:
        for item in os.listdir(directory_from):
            source_item = os.path.join(directory_from, item)
            target_item = os.path.join(directory_to, item)
            
            if os.path.isfile(source_item):
                shutil.copy2(source_item, target_item)  # copy2 preserves metadata
            elif os.path.isdir(source_item):
                if os.path.exists(target_item):
                    # If directory already exists, copy contents
                    for subitem in os.listdir(source_item):
                        sub_source = os.path.join(source_item, subitem)
                        sub_target = os.path.join(target_item, subitem)
                        if os.path.isfile(sub_source):
                            shutil.copy2(sub_source, sub_target)
                else:
                    # Create new directory with copytree using copy_function to avoid recursion
                    shutil.copytree(source_item, target_item, copy_function=shutil.copy2)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when copying files: {e}")
    except OSError as e:
        raise OSError(f"Error occurred while copying files: {e}")

# Unittests
