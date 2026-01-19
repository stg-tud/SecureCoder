import logging
import os
import zipfile
from datetime import datetime

def compress_logs(logs_directory: str, destination_dir: str, logger: logging.Logger) -> None:
    """
    Archives log files from a given directory into a .zip file and saves it to the destination directory.

    Args:
        logs_directory (str): The directory where log files are stored.
        destination_dir (str): The destination directory where the zip archive will be placed.
        logger (logging.Logger): Logger instance to record progress and errors.

    Returns:
        None

    Raises:
        Errors are logged but not raised.
    """
    try:
        # Validate input directories
        if not os.path.isdir(logs_directory):
            logger.error(f"Logs directory does not exist: {logs_directory}")
            return

        if not os.path.isdir(destination_dir):
            logger.error(f"Destination directory does not exist: {destination_dir}")
            return

        # Create a unique zip file name using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"logs_backup_{timestamp}.zip"
        zip_path = os.path.join(destination_dir, zip_filename)

        # Create zip archive using the zipfile module (secure, no shell injection risk)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(logs_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Preserve directory structure inside the zip relative to logs_directory
                    arcname = os.path.relpath(file_path, logs_directory)
                    zipf.write(file_path, arcname)

        logger.info(f"Log archive created successfully: {zip_path}")

    except Exception as e:
        logger.error(f"Failed to compress logs: {str(e)}")

# Unittests
