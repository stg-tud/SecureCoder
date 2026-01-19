def gather_project_dependencies(req_file_path: str) -> None:
    """
    The purpose of this function is to analyze and collect the dependencies of a project, writing them to a specified requirements file.
    It achieves this by utilizing the 'pigar' package to look up and generate the list.

    Args:
        req_file_path (str): The location of the file where the list of dependencies will be written.

    Raises:
        ModuleNotFoundError: if the 'pigar' package is unavailable.

    Returns:
        None

    Note:
        Logs errors if dependency collection fails, but no exceptions (apart from ModuleNotFoundError) are explicitly raised.
    """
    import logging
    import os
    from pathlib import Path

    try:
        import pigar
    except ModuleNotFoundError:
        logger.error("The 'pigar' package is required to gather dependencies but is not installed.")
        raise

    # Validate and resolve the requirements file path
    try:
        req_path = Path(req_file_path).resolve()
        # Ensure the parent directory exists
        req_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to process the requirements file path '{req_file_path}': {e}")
        return

    # Use pigar programmatically if possible, avoiding subprocess shell usage
    try:
        # pigar does not provide a stable public API for direct import usage,
        # so we may need to invoke it via command line safely.
        # We avoid shell=True and pass the command as a list to prevent injection.

        from subprocess import run

        # Build command safely as a list to avoid shell injection
        cmd = [
            "pigar",
            "generate",
            "-o", str(req_path),
        ]

        result = run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"pigar failed to generate requirements: {result.stderr}")
        else:
            logger.info(f"Dependency list successfully written to {req_path}")

    except Exception as e:
        logger.error(f"An error occurred while gathering dependencies: {e}")