def create_backup(folder_path: str, archive_name: str):
    """
    Creates a compressed tar.gz archive of the specified directory using the tar command.

    Args:
        folder_path (str): Specifies the path to the directory that needs to be archived.
        archive_name (str): The desired name for the resulting backup file (without the extension).

    Raises:
        OSError: If the tar command fails during execution.
    
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

    # Construct the archive file name with .tar.gz extension
    archive_filename = f"{archive_name}.tar.gz"

    # Build the command as a list to avoid shell injection
    cmd = [
        "tar",
        "-czf",
        archive_filename,
        "-C",
        os.path.dirname(folder_path),
        os.path.basename(folder_path)
    ]

    try:
        # Execute the command securely using subprocess.run with a list
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Backup created successfully: {archive_filename}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create backup: {e.stderr.strip()}")
        raise OSError(f"Failed to create backup using tar: {e.stderr.strip()}") from e
    except Exception as e:
        logger.error(f"Unexpected error during backup creation: {str(e)}")
        raise OSError(f"Unexpected error during backup creation: {str(e)}") from e