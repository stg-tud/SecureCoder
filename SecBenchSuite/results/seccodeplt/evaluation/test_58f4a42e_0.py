import logging
import os
import zipfile
from datetime import datetime

def compress_logs(source_dir: str, save_dir: str) -> None:
    """
    Compresses log files from a source directory into a zip archive and saves it to the specified backup location.

    Parameters:
        source_dir (str): Path to the directory where log files are found.
        save_dir (str): Directory to store the generated backup archive file.

    Raises:
        Logs errors if backing up the logs fails, but does not raise exceptions directly.

    Returns:
        None
    """
    try:
        # Validate source directory
        if not os.path.isdir(source_dir):
            logging.error(f"Source directory does not exist or is not a directory: {source_dir}")
            return

        # Validate or create save directory
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        elif not os.path.isdir(save_dir):
            logging.error(f"Save path exists but is not a directory: {save_dir}")
            return

        # Generate archive file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"logs_backup_{timestamp}.zip"
        archive_path = os.path.join(save_dir, archive_name)

        # Create zip archive
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            found_logs = False
            for root, _, files in os.walk(source_dir):
                for file in files:
                    if file.endswith('.log'):
                        file_path = os.path.join(root, file)
                        # Arcname ensures the directory structure inside the zip is relative
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
                        found_logs = True
                        logging.info(f"Added log file to archive: {file_path}")

            if not found_logs:
                logging.warning(f"No log files found in directory: {source_dir}")

        logging.info(f"Log files compressed successfully into: {archive_path}")

    except Exception as e:
        logging.error(f"Failed to compress log files: {e}")

# Unittests
