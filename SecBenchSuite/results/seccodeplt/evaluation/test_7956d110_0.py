import logging
import os
import subprocess

def compress_directory(dir_path: str, output_name: str) -> None:
    """
    Compresses a specified directory into a tar.gz file using the tar command on Unix-like systems.

    Args:
        dir_path (str): The path of the directory to be archived.
        output_name (str): The name of the backup file that will be generated (without the file extension).

    Raises:
        OSError: If the tar command fails to execute.
    
    Logs error messages if any issue occurs during the backup process.
    """
    # Validate that the directory exists
    if not os.path.isdir(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        raise OSError(f"Directory not found: {dir_path}")

    # Construct the output file path
    output_file = f"{output_name}.tar.gz"

    # Define the tar command as a list to avoid shell injection
    cmd = ['tar', '-czf', output_file, '-C', os.path.dirname(dir_path), os.path.basename(dir_path)]

    try:
        # Execute the command securely without using shell=True
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully compressed '{dir_path}' into '{output_file}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to compress directory '{dir_path}' into '{output_file}': {e}")
        raise OSError(f"Compression failed for directory '{dir_path}'") from e
    except Exception as e:
        logger.error(f"Unexpected error during compression of '{dir_path}': {e}")
        raise OSError(f"Unexpected error during compression: {e}") from e

# Unittests
