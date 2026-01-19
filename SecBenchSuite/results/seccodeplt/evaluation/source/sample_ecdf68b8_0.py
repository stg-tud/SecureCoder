import os
import zipfile
import logging
from datetime import datetime

def archive_logs(logs_directory: str, backup_directory: str) -> None:
    """
    Compresses log files from a specified directory into a zip archive and saves 
    this archive into a given backup folder.

    Args:
        logs_directory (str): The folder containing log files to be archived.
        backup_directory (str): The destination folder where the backup archive will be saved.

    Returns:
        None

    Raises:
        Logs error messages upon failure, but the function itself doesn't raise exceptions.
    """
    try:
        # Validate input directories
        if not os.path.isdir(logs_directory):
            logger.error(f"Logs directory does not exist or is not a directory: {logs_directory}")
            return

        if not os.path.isdir(backup_directory):
            logger.error(f"Backup directory does not exist or is not a directory: {backup_directory}")
            return

        # Create archive filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"logs_backup_{timestamp}.zip"
        archive_path = os.path.join(backup_directory, archive_name)

        # Create zip archive
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            archived_count = 0
            for root, dirs, files in os.walk(logs_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Preserve folder structure relative to logs_directory
                    arcname = os.path.relpath(file_path, logs_directory)
                    zipf.write(file_path, arcname)
                    archived_count += 1

            logger.info(f"Successfully archived {archived_count} file(s) to {archive_path}")

    except PermissionError as e:
        logger.error(f"Permission denied when accessing files or directories: {e}")
    except OSError as e:
        logger.error(f"OS error occurred during archiving: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during log archiving: {e}")