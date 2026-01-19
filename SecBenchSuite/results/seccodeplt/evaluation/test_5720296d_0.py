import os
import subprocess
import logging

def generate_backup(target_directory: str, tar_name: str) -> None:
    """
    Generates a compressed tar.gz archive of the specified directory using the tar command.

    Args:
        target_directory (str): Specifies the path to the directory that needs to be archived.
        tar_name (str): The desired name for the resulting backup file (without the extension).

    Raises:
        OSError: If the tar command fails during processing.
    
    Logs:
        Logs error messages if the backup process fails.
    """
    # Validate that the target directory exists and is a directory
    if not os.path.exists(target_directory):
        logger.error(f"Target directory does not exist: {target_directory}")
        raise OSError(f"Target directory does not exist: {target_directory}")
    
    if not os.path.isdir(target_directory):
        logger.error(f"Target path is not a directory: {target_directory}")
        raise OSError(f"Target path is not a directory: {target_directory}")

    # Construct the output filename with .tar.gz extension
    tar_filename = f"{tar_name}.tar.gz"

    # Build the command as a list to avoid shell injection
    cmd = ['tar', '-czf', tar_filename, '-C', target_directory, '.']

    try:
        # Execute the command safely without shell=True
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Backup successfully created: {tar_filename}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create backup for '{target_directory}'. "
                     f"Command '{' '.join(cmd)}' returned non-zero exit status {e.returncode}. "
                     f"stderr: {e.stderr.decode()}")
        raise OSError(f"Failed to create backup: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during backup of '{target_directory}': {str(e)}")
        raise OSError(f"Unexpected error during backup: {e}") from e

# Unittests
