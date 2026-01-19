import os
import zipfile
import logging
from datetime import datetime

def create_log_backup(log_path: str, archive_path: str) -> None:
    """
    Compresses log files from a specified directory into a zip archive and saves 
    this archive into a given backup folder.

    Args:
        log_path (str): The folder containing log files to be archived.
        archive_path (str): The destination folder where the backup archive will be saved.
    
    Returns:
        None
    
    Raises:
        Logs error messages upon failure, but the function itself doesn't raise exceptions.
    """
    try:
        # Validate source directory
        if not os.path.exists(log_path):
            logger.error(f"Log directory does not exist: {log_path}")
            return
        if not os.path.isdir(log_path):
            logger.error(f"Log path is not a directory: {log_path}")
            return

        # Ensure archive directory exists
        os.makedirs(archive_path, exist_ok=True)

        # Define archive file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"logs_backup_{timestamp}.zip"
        archive_file_path = os.path.join(archive_path, archive_filename)

        # Create zip archive
        with zipfile.ZipFile(archive_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            logger.info(f"Starting backup of logs from {log_path} to {archive_file_path}")
            file_count = 0
            for root, dirs, files in os.walk(log_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Preserve directory structure inside the archive
                    arcname = os.path.relpath(file_path, log_path)
                    zipf.write(file_path, arcname)
                    file_count += 1
            logger.info(f"Successfully archived {file_count} files.")
        
        logger.info(f"Log backup completed: {archive_file_path}")

    except Exception as e:
        logger.error(f"Failed to create log backup: {str(e)}", exc_info=True)