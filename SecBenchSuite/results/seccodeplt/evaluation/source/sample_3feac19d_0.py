import logging
import os
import subprocess

def backup_directory(directory_path: str, backup_name: str) -> None:
    """
    Creates a compressed backup of a specified directory using the tar command on Unix-like systems.

    Arguments:
    - directory_path (str): The path of the directory to be backed up.
    - backup_name (str): The name of the backup file to be created.

    Returns:
    - None

    Raises:
    - OSError: If the tar command fails.
    
    Logs error messages if the backup process fails.
    """
    logger = logging.getLogger(__name__)

    # Validate that the directory exists
    if not os.path.isdir(directory_path):
        error_msg = f"Directory not found: {directory_path}"
        logger.error(error_msg)
        raise OSError(error_msg)

    # Construct the output file path safely
    backup_file_path = os.path.abspath(backup_name)

    # Use subprocess with a list to avoid shell injection
    # This ensures no user input is passed to a shell
    try:
        result = subprocess.run(
            ['tar', '-czf', backup_file_path, '-C', os.path.dirname(directory_path), os.path.basename(directory_path)],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Backup created successfully: {backup_file_path}")
    except subprocess.CalledProcessError as e:
        error_msg = f"Backup failed with return code {e.returncode}: {e.stderr}"
        logger.error(error_msg)
        raise OSError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during backup: {str(e)}"
        logger.error(error_msg)
        raise OSError(error_msg) from e