import os
import subprocess
import logging

def archive_directory(dir_path: str, output_name: str) -> None:
    """
    Creates a compressed tar.gz archive of the specified directory using the tar command.

    Args:
        dir_path (str): Specifies the path to the directory that needs to be archived.
        output_name (str): The desired name for the resulting backup file (without the extension).

    Raises:
        OSError: If the tar command fails during execution.
    
    Logs:
        Error messages if directory does not exist or archiving fails.
    
    Returns:
        None
    """
    logger = logging.getLogger(__name__)

    # Validate that the directory exists
    if not os.path.isdir(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        raise OSError(f"Directory not found: {dir_path}")

    # Construct the output file path
    output_file = f"{output_name}.tar.gz"

    # Use a list to prevent shell injection (security best practice)
    cmd = ['tar', '-czf', output_file, '-C', os.path.dirname(dir_path), os.path.basename(dir_path)]

    try:
        # Execute the tar command securely without shell=True
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully archived {dir_path} to {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to archive directory {dir_path}: {e}")
        raise OSError(f"Archiving failed for {dir_path}") from e
    except Exception as e:
        logger.error(f"Unexpected error during archiving {dir_path}: {e}")
        raise OSError(f"Unexpected error while archiving {dir_path}") from e