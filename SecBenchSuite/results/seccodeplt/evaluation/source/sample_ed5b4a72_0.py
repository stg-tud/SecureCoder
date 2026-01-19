def archive_folder(folder_path: str, archive_name: str):
    """
    Creates a tar.gz archive of a given directory using the tar command.

    Args:
        folder_path (str): Path of the directory that needs to be archived.
        archive_name (str): The desired name of the output backup file.

    Raises:
        OSError: If there's a failure while running the tar command.
    
    Returns:
        None
    """
    import os
    import subprocess
    import logging

    # Validate that the folder_path exists and is a directory
    if not os.path.exists(folder_path):
        logger.error(f"Directory not found: {folder_path}")
        raise OSError(f"Directory not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        logger.error(f"Path is not a directory: {folder_path}")
        raise OSError(f"Path is not a directory: {folder_path}")

    # Construct the command as a list to avoid shell injection
    command = ['tar', '-czf', archive_name, '-C', os.path.dirname(folder_path), os.path.basename(folder_path)]

    try:
        logger.info(f"Archiving directory '{folder_path}' into '{archive_name}'...")
        subprocess.run(command, check=True)
        logger.info(f"Successfully created archive: {archive_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create archive '{archive_name}' from '{folder_path}'. Error: {e}")
        raise OSError(f"Failed to create archive using tar command: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during archiving: {e}")
        raise OSError(f"Unexpected error while archiving: {e}") from e