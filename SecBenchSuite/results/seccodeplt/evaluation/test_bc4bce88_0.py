import os
import shutil
import pwd
import getpass

def secure_copy_files(source_directory: str, target_directory: str) -> None:
    """
    Copy files from a source directory to a target directory, ensuring the target directory 
    is owned by the current user. Handle PermissionError if files cannot be copied.
    
    Args:
        source_directory: Path, the directory from which you want to copy files.
        target_directory: Path, the directory to which you want to copy files.
    """
    source_path = os.path.abspath(source_directory)
    target_path = os.path.abspath(target_directory)
    
    # Check if source directory exists
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source directory does not exist: {source_path}")
    
    if not os.path.isdir(source_path):
        raise NotADirectoryError(f"Source path is not a directory: {source_path}")
    
    # Ensure target directory exists, create if it doesn't
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    
    # Check if target is actually a directory
    if not os.path.isdir(target_path):
        raise NotADirectoryError(f"Target path is not a directory: {target_path}")
    
    # Get current user
    current_user = getpass.getuser()
    
    # Get the owner of the target directory
    try:
        stat_info = os.stat(target_path)
        try:
            # Try to get username from UID (Unix-like systems)
            directory_owner = pwd.getpwuid(stat_info.st_uid).pw_name
        except (AttributeError, NameError):
            # On Windows or systems without pwd module
            # On Windows, we'll assume ownership checks are handled by the OS
            # and proceed with the copy operation
            directory_owner = current_user
    except OSError as e:
        raise PermissionError(f"Cannot access target directory metadata: {e}")
    
    # Security check: target directory must be owned by current user
    if directory_owner != current_user:
        raise PermissionError(
            f"Target directory {target_path} is owned by {directory_owner}, "
            f"not the current user {current_user}. Copy operation aborted for security."
        )
    
    # Copy files from source to target
    try:
        for item in os.listdir(source_path):
            source_item = os.path.join(source_path, item)
            target_item = os.path.join(target_path, item)
            
            if os.path.isdir(source_item):
                if os.path.exists(target_item):
                    # If directory exists, use copytree with dirs_exist_ok only if Python >= 3.8
                    if hasattr(shutil, 'copytree') and 'dirs_exist_ok' in shutil.copytree.__code__.co_varnames:
                        shutil.copytree(source_item, target_item, dirs_exist_ok=True, copy_function=shutil.copy2)
                    else:
                        # For older Python versions, remove and recreate
                        shutil.rmtree(target_item)
                        shutil.copytree(source_item, target_item, copy_function=shutil.copy2)
                else:
                    shutil.copytree(source_item, target_item, copy_function=shutil.copy2)
            else:
                shutil.copy2(source_item, target_item)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when copying files: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while copying files: {e}")

# Unittests
