import logging
import os
import zipfile
from datetime import datetime

def archive_logs(logs_folder: str, archive_dir: str, logger: logging.Logger) -> None:
    """
    Archives log files from a given directory into a .zip format and saves the archive
    in a specified backup location.

    Args:
        logs_folder (str): The directory where log files are stored.
        archive_dir (str): The destination directory where the zip archive will be placed.
        logger (logging.Logger): An instance of logging.Logger to record log messages.

    Returns:
        None

    Raises:
        Logs errors if archiving fails, but does not raise exceptions.
    """
    try:
        # Validate input directories
        if not os.path.isdir(logs_folder):
            logger.error(f"Logs folder does not exist: {logs_folder}")
            return

        if not os.path.isdir(archive_dir):
            logger.error(f"Archive directory does not exist: {archive_dir}")
            return

        # Create a timestamped archive filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"logs_archive_{timestamp}.zip"
        archive_path = os.path.join(archive_dir, archive_name)

        # Create the zip archive using the zipfile module (secure, no shell injection)
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(logs_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Preserve folder structure inside the archive relative to logs_folder
                    arcname = os.path.relpath(file_path, logs_folder)
                    zipf.write(file_path, arcname)

        logger.info(f"Log files successfully archived to {archive_path}")

    except Exception as e:
        logger.error(f"Failed to archive log files: {str(e)}")

# Unittests
