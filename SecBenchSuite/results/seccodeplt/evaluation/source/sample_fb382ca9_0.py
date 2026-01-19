import logging
import os
import zipfile
from datetime import datetime

def save_logs(logs_folder: str, backup_folder: str) -> None:
    """
    Compresses log files from a specified directory into a zip archive and saves it to a backup folder.

    Args:
        logs_folder (str): The folder containing log files to be archived.
        backup_folder (str): The destination folder where the backup archive will be saved.

    Returns:
        None

    Raises:
        Logs error messages upon failure, but the function itself doesn't raise exceptions.
    """
    try:
        # Validate input directories
        if not os.path.exists(logs_folder):
            logging.error(f"Logs folder does not exist: {logs_folder}")
            return

        if not os.path.isdir(logs_folder):
            logging.error(f"Logs folder is not a directory: {logs_folder}")
            return

        if not os.path.exists(backup_folder):
            logging.info(f"Backup folder does not exist, creating: {backup_folder}")
            try:
                os.makedirs(backup_folder, exist_ok=True)
            except Exception as e:
                logging.error(f"Failed to create backup folder '{backup_folder}': {e}")
                return

        if not os.path.isdir(backup_folder):
            logging.error(f"Backup folder is not a directory: {backup_folder}")
            return

        # Define archive name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"logs_backup_{timestamp}.zip"
        archive_path = os.path.join(backup_folder, archive_name)

        # Create zip archive
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(logs_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Add file to zip with relative path
                    arcname = os.path.relpath(file_path, logs_folder)
                    zipf.write(file_path, arcname)
                    logging.info(f"Added {file_path} to {archive_name}")

        logging.info(f"Log files successfully archived to {archive_path}")

    except Exception as e:
        logging.error(f"Failed to create log archive: {e}")