def compress_directory(dir_path: str, compressed_name: str) -> None:
    """
    Creates a tar.gz archive of a given directory using the tar command.

    Args:
        dir_path (str): Path of the directory that needs to be archived.
        compressed_name (str): The desired name of the output backup file.

    Raises:
        OSError: If there's a failure while running the tar command.
                 Logs error messages upon failure during the backup process.

    Returns:
        None
    """
    import os
    import subprocess
    import logging

    # Validate input paths
    if not os.path.isdir(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        raise OSError(f"Directory not found: {dir_path}")

    # Ensure the compressed_name ends with .tar.gz
    if not compressed_name.endswith(".tar.gz"):
        compressed_name += ".tar.gz"

    # Use a list to avoid shell injection; safe for untrusted input
    cmd = ["tar", "-czf", compressed_name, "-C", os.path.dirname(dir_path), os.path.basename(dir_path)]

    try:
        logger.info(f"Archiving directory '{dir_path}' to '{compressed_name}'")
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Successfully archived '{dir_path}' to '{compressed_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to archive directory '{dir_path}'. Error: {e.stderr.decode()}")
        raise OSError(f"Failed to create archive '{compressed_name}' from '{dir_path}'") from e
    except Exception as e:
        logger.error(f"Unexpected error during archiving: {e}")
        raise OSError(f"Unexpected error while archiving '{dir_path}'") from e