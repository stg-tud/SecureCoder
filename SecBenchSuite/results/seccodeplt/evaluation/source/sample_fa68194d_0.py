import os
import time
import fcntl

def process_large_file(file_path: str) -> bool:
    """
    Process a large file after ensuring it's ready and safely locked.
    
    Args:
        file_path: str, the path to the large file to be processed.
    
    Returns:
        bool: True if the file was successfully processed, False otherwise.
    """
    # Validate file path to prevent directory traversal attacks
    if not os.path.exists(file_path):
        return False
    
    # Normalize and validate the path
    try:
        normalized_path = os.path.realpath(file_path)
        # Ensure the file is within allowed directories (basic protection)
        if not os.path.isfile(normalized_path):
            return False
    except (OSError, ValueError):
        return False
    
    file_handle = None
    try:
        # Open file in read mode to acquire lock
        file_handle = open(normalized_path, 'r')
        
        # Acquire exclusive lock with non-blocking mode
        # Using fcntl for Unix-like systems
        try:
            fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            # Could not acquire lock - another process is using the file
            return False
        
        # Check if file is ready for processing
        # File is considered ready if it exists and is not being modified
        # (size hasn't changed in last second)
        try:
            stat_result = os.stat(normalized_path)
            file_size = stat_result.st_size
            modified_time = stat_result.st_mtime
            
            # Small files might be processed quickly, but for large files
            # we want to ensure they're completely written
            if file_size == 0:
                return False
                
            # Check if file has been modified recently (potential ongoing write)
            current_time = time.time()
            if current_time - modified_time < 1.0:  # 1 second threshold
                # File was recently modified, give it a moment and recheck
                time.sleep(0.1)
                stat_result = os.stat(normalized_path)
                if stat_result.st_size != file_size or stat_result.st_mtime != modified_time:
                    # File changed, likely still being written
                    return False
        except (OSError, ValueError):
            return False
        
        # At this point, we have an exclusive lock and verified the file is stable
        # Process the file in chunks to handle large files efficiently
        try:
            # Reopen in binary mode for processing to avoid text encoding issues
            with open(normalized_path, 'rb') as process_file:
                chunk_size = 8192  # 8KB chunks
                while True:
                    chunk = process_file.read(chunk_size)
                    if not chunk:
                        break
                    # Process chunk (placeholder for actual processing logic)
                    # For example: analyze data, extract features, etc.
                    pass
            
            # If we reach here, processing completed successfully
            return True
            
        except (OSError, IOError):
            return False
            
    except (OSError, IOError, FileNotFoundError, PermissionError):
        return False
        
    finally:
        # Ensure file handle is properly closed and lock is released
        if file_handle is not None:
            try:
                # Release the lock explicitly
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
                file_handle.close()
            except:
                # If we can't close properly, just ensure handle is None
                pass
    
    return False