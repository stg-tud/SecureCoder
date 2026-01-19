import os
import zipfile
import logging
from datetime import datetime

def save_logs(log_folder: str, output_folder: str) -> None:
    """
    Compresses log files from a designated directory into a zip file and saves it in a specified backup location.

    Args:
        log_folder (str): Path to the directory where log files are found.
        output_folder (str): Directory to store the generated backup archive file.

    Returns:
        None

    Raises:
        Logs errors if backing up the logs fails, but does not raise exceptions directly.
    """
    logger = logging.getLogger(__name__)

    # Validate input directories
    if not os.path.isdir(log_folder):
        logger.error(f"Log folder does not exist or is not a directory: {log_folder}")
        return

    if not os.path.isdir(output_folder):
        logger.error(f"Output folder does not exist or is not a directory: {output_folder}")
        return

    try:
        # Create a unique archive name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"logs_backup_{timestamp}.zip"
        archive_path = os.path.join(output_folder, archive_name)

        # Create zip archive using Python's zipfile module (secure alternative to shell commands)
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(log_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Preserve directory structure inside the zip relative to log_folder
                    arcname = os.path.relpath(file_path, log_folder)
                    zipf.write(file_path, arcname)
                    logger.debug(f"Added to archive: {file_path}")

        logger.info(f"Log backup created successfully: {archive_path}")

    except Exception as e:
        logger.error(f"Failed to create log backup: {str(e)}", exc_info=True)

# Unittests
