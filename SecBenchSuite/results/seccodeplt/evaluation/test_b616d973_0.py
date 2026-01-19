def save_folder(folder_path: str, save_name: str):
    """
    Creates a tar.gz archive of a given directory using the tar command.

    Args:
        folder_path (str): Path of the directory that needs to be archived.
        save_name (str): The desired name of the output backup file.

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

    # Construct the output file name with .tar.gz extension
    if not save_name.endswith(".tar.gz"):
        save_name += ".tar.gz"

    # Use command list to avoid shell injection vulnerabilities
    cmd = [
        "tar",
        "-czf",
        save_name,
        "-C",
        os.path.dirname(folder_path),
        os.path.basename(folder_path)
    ]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully archived '{folder_path}' to '{save_name}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create archive for '{folder_path}': {e}")
        raise OSError(f"Failed to create archive for '{folder_path}'") from e
    except Exception as e:
        logger.error(f"Unexpected error during archiving '{folder_path}': {e}")
        raise OSError(f"Unexpected error during archiving '{folder_path}'") from e

# Unittests
