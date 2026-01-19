import os
import zipfile
import logging
from datetime import datetime

def archive_logs(log_directory: str, destination_directory: str, logger: logging.Logger) -> None:
    """
    Compresses log files from a designated directory into a zip file and saves it in a specified backup location.

    Args:
        log_directory (str): Path to the directory where log files are found.
        destination_directory (str): Directory to store the generated backup archive file.
        logger (logging.Logger): Logger object to track operations.

    Returns:
        None

    Raises:
        Logs errors if backing up the logs fails, but does not raise exceptions directly.
    """
    try:
        # Validate input directories
        if not os.path.isdir(log_directory):
            logger.error(f"Log directory does not exist: {log_directory}")
            return

        if not os.path.isdir(destination_directory):
            logger.error(f"Destination directory does not exist: {destination_directory}")
            return

        # Create a timestamped archive filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"logs_backup_{timestamp}.zip"
        archive_path = os.path.join(destination_directory, archive_filename)

        # Create the archive and add log files
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            log_file_count = 0
            for root, _, files in os.walk(log_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Optional: filter only log files by extension if desired
                    # if file.lower().endswith('.log'):
                    arcname = os.path.relpath(file_path, log_directory)
                    zipf.write(file_path, arcname)
                    log_file_count += 1
                    logger.debug(f"Added log file to archive: {arcname}")

            if log_file_count == 0:
                logger.warning(f"No files found to archive in: {log_directory}")
            else:
                logger.info(f"Successfully archived {log_file_count} log file(s) to {archive_path}")

    except Exception as e:
        logger.error(f"Failed to archive log files: {str(e)}", exc_info=True)

# Unittests
