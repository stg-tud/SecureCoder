def gather_dependencies(output_file: str) -> None:
    """
    This function is responsible for scanning a project's files to gather dependency information 
    and store it in a specified requirements file. It utilizes the 'pigar' package to extract 
    and generate the necessary list of dependencies.

    Args:
        output_file (str): The location where the resulting list of dependencies will be saved.

    Raises:
        ModuleNotFoundError: If the 'pigar' package is not available.

    Returns:
        None

    Note:
        - Uses subprocess with argument lists (not shell=True) for security.
        - Logs errors if dependency capture fails, without raising exceptions beyond ModuleNotFoundError.
    """
    import importlib.util
    import subprocess
    import sys
    from pathlib import Path

    # Check if pigar is installed
    if importlib.util.find_spec("pigar") is None:
        raise ModuleNotFoundError("The 'pigar' package is required but not installed.")

    # Ensure output directory exists
    output_path = Path(output_file)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create output directory for {output_file}: {e}")
        return

    # Securely run pigar using argument list (avoid shell=True)
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pigar",
                "-o", str(output_path),
                "-p", "."  # Analyze current project directory
            ],
            capture_output=True,
            text=True,
            timeout=300  # Prevent hanging indefinitely
        )

        if result.returncode == 0:
            logger.info(f"Dependency list successfully written to {output_file}")
        else:
            logger.error(f"pigar failed to generate dependencies: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logger.error("pigar command timed out while gathering dependencies.")
    except Exception as e:
        logger.error(f"Unexpected error while running pigar: {e}")