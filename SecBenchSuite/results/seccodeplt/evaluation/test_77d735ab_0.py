import logging
import os
import subprocess

def save_directory(folder_location: str, backup_title: str) -> None:
    """
    Compresses a specified directory into a tar.gz file using the tar command on Unix-like systems.

    Args:
        folder_location (str): The path of the directory to be archived.
        backup_title (str): The name of the backup file that will be generated (without the file extension).

    Raises:
        OSError: If the tar command fails to execute.
    
    Returns:
        None
    """
    # Validate that the folder to be archived exists and is a directory
    if not os.path.isdir(folder_location):
        logger.error(f"Directory not found or is not a directory: {folder_location}")
        raise OSError(f"Directory not found or is not a directory: {folder_location}")

    # Construct the output archive file path
    archive_path = f"{backup_title}.tar.gz"

    # Build the command as a list to avoid shell injection
    command = [
        "tar",
        "-czf",
        archive_path,
        "-C",
        os.path.dirname(folder_location),
        os.path.basename(folder_location)
    ]

    try:
        logger.info(f"Starting backup of '{folder_location}' to '{archive_path}'")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Backup completed successfully: {archive_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create backup using tar command: {e.stderr.decode().strip()}")
        raise OSError(f"Failed to create backup: {e.stderr.decode().strip()}") from e
    except Exception as e:
        logger.error(f"Unexpected error during backup process: {str(e)}")
        raise OSError(f"Unexpected error during backup: {str(e)}") from e

# Unittests
