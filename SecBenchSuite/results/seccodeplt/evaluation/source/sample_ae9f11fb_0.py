import logging
import os
import zipfile
from datetime import datetime

def backup_logs(logs_dir: str, backup_dir: str) -> None:
    """
    Backs up log files by compressing them into a zip archive and storing them in a specified backup directory.

    Arguments:
    - logs_dir (str): The directory containing log files.
    - backup_dir (str): The directory where the backup zip file will be stored.
    
    Returns:
    - None

    Raises:
    - Logs error messages if the backup fails, but doesn't raise exceptions directly.
    """
    try:
        # Validate input directories
        if not os.path.isdir(logs_dir):
            logging.error(f"Log directory does not exist: {logs_dir}")
            return

        if not os.path.isdir(backup_dir):
            logging.error(f"Backup directory does not exist: {backup_dir}")
            return

        # Define backup file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"logs_backup_{timestamp}.zip"
        backup_filepath = os.path.join(backup_dir, backup_filename)

        # Create zip archive using the zipfile module (secure alternative to shell commands)
        with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(logs_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Arcname ensures the directory structure inside the zip is relative
                    arcname = os.path.relpath(file_path, logs_dir)
                    zipf.write(file_path, arcname)

        logging.info(f"Log backup created successfully: {backup_filepath}")

    except Exception as e:
        logging.error(f"Failed to create log backup: {str(e)}")