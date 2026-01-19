def fetch_project_dependencies(dep_file_path: str) -> None:
    """
    The purpose of this function is to analyze and collect the dependencies of a project, writing them to a specified requirements file.
    It achieves this by utilizing the 'pigar' package to look up and generate the list.

    Args:
        dep_file_path (str): The location of the file where the list of dependencies will be written.

    Raises:
        ModuleNotFoundError: If the 'pigar' package is unavailable.

    Returns:
        None

    Security Note:
        This function avoids using shell=True or os.system to prevent injection risks. It uses subprocess with a command list.
    """
    import logging
    import os
    from pathlib import Path
    import subprocess

    # Ensure pigar is available
    try:
        import pigar  # noqa: F401
    except ImportError:
        raise ModuleNotFoundError("The 'pigar' package is required to collect dependencies. Install it using 'pip install pigar'.")

    try:
        # Convert to absolute path and ensure parent directories exist
        output_path = Path(dep_file_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build command as a list to avoid shell injection
        command = [
            'pigar',
            'generate',
            '-f', str(output_path),
            '-o', '.',  # assume current directory as project root
        ]

        # Execute the command safely without shell=True
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"pigar command failed with return code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            logger.info(f"stdout: {result.stdout}")
        else:
            logger.info(f"Dependencies successfully written to {dep_file_path}")

    except Exception as e:
        logger.error(f"Failed to collect project dependencies: {e}")