import os
import zipfile
import logging
from datetime import datetime

def store_logs(source_logs: str, target_backup_dir: str, logger: logging.Logger) -> None:
    """
    Archives log files from the source directory into a zip file and stores it in the target backup directory.

    Args:
        source_logs (str): The directory where log files are stored.
        target_backup_dir (str): The destination directory where the zip archive will be placed.
        logger (logging.Logger): Logger instance to record execution messages.

    Returns:
        None

    Raises:
        Errors are logged but not raised.
    """
    try:
        # Validate source directory exists and is a directory
        if not os.path.exists(source_logs):
            logger.error(f"Source log directory does not exist: {source_logs}")
            return
        if not os.path.isdir(source_logs):
            logger.error(f"Source path is not a directory: {source_logs}")
            return

        # Create target backup directory if it doesn't exist
        if not os.path.exists(target_backup_dir):
            os.makedirs(target_backup_dir, exist_ok=True)
        elif not os.path.isdir(target_backup_dir):
            logger.error(f"Target backup path is not a directory: {target_backup_dir}")
            return

        # Define the name of the zip file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"logs_backup_{timestamp}.zip"
        zip_filepath = os.path.join(target_backup_dir, zip_filename)

        # Create the zip archive using the zipfile module (secure alternative to shell commands)
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_logs):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Preserve directory structure inside the archive
                    arcname = os.path.relpath(file_path, source_logs)
                    zipf.write(file_path, arcname)

        logger.info(f"Log archive created successfully: {zip_filepath}")

    except Exception as e:
        logger.error(f"Failed to create log archive: {str(e)}", exc_info=True)

# Unittests
