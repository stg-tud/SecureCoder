import logging
import os
import subprocess

def archive_folder(folder_path: str, archive_name: str) -> None:
    """
    Compresses a specified directory into a tar.gz file using the tar command on Unix-like systems.

    Args:
        folder_path (str): The path of the directory to be archived.
        archive_name (str): The name of the backup file that will be generated (without the file extension).

    Raises:
        OSError: If the tar command fails to execute.
    
    Logs error messages if any issue occurs during the backup process.
    """
    # Validate inputs to ensure they are strings and paths are not empty
    if not isinstance(folder_path, str) or not folder_path.strip():
        logger.error("Invalid folder_path: must be a non-empty string.")
        raise ValueError("folder_path must be a non-empty string.")
    
    if not isinstance(archive_name, str) or not archive_name.strip():
        logger.error("Invalid archive_name: must be a non-empty string.")
        raise ValueError("archive_name must be a non-empty string.")
    
    folder_path = folder_path.strip()
    archive_name = archive_name.strip()

    # Ensure the folder exists and is a directory
    if not os.path.exists(folder_path):
        logger.error(f"Folder does not exist: {folder_path}")
        raise OSError(f"Folder does not exist: {folder_path}")
    
    if not os.path.isdir(folder_path):
        logger.error(f"Path is not a directory: {folder_path}")
        raise OSError(f"Path is not a directory: {folder_path}")

    # Construct the archive file path
    archive_path = f"{archive_name}.tar.gz"

    # Build the command as a list to avoid shell injection
    cmd = [
        "tar", 
        "-czf", 
        archive_path, 
        "-C", 
        os.path.dirname(folder_path), 
        os.path.basename(folder_path)
    ]

    try:
        logger.info(f"Archiving folder '{folder_path}' to '{archive_path}'...")
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully archived '{folder_path}' to '{archive_path}'.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to archive folder '{folder_path}'. Command failed with return code {e.returncode}.")
        raise OSError(f"Failed to create archive for '{folder_path}'.") from e
    except Exception as e:
        logger.error(f"Unexpected error while archiving folder '{folder_path}': {str(e)}")
        raise OSError(f"Unexpected error during archiving: {str(e)}") from e

# Unittests
