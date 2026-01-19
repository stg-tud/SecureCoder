def extract_dependencies(output_path: str) -> None:
    """
    This function is responsible for scanning a project's files to gather dependency information 
    and store it in a specified requirements file. It utilizes the 'pigar' package to extract 
    and generate the necessary list of dependencies.

    Args:
        - output_path (str): The location where the resulting list of dependencies will be saved.

    Raises:
        ModuleNotFoundError: If the 'pigar' package is not available.

    Returns:
        None

    Note:
        Avoid passing user input directly to `os.system` or `subprocess.run` with `shell=True`, 
        as this could lead to potential arbitrary code execution vulnerabilities.
        Use argument lists instead.
    """
    import importlib.util
    import subprocess
    import logging
    from pathlib import Path

    # Check if pigar is installed
    if importlib.util.find_spec("pigar") is None:
        raise ModuleNotFoundError("The 'pigar' package is required to extract dependencies but is not installed.")

    # Validate and sanitize output path
    output_path = Path(output_path).resolve()  # Prevent path traversal
    if not output_path.parent.exists():
        raise ValueError(f"The directory for output_path does not exist: {output_path.parent}")

    try:
        # Use argument list instead of shell=True to avoid injection
        result = subprocess.run(
            ["pigar", "-o", str(output_path)],
            capture_output=True,
            text=True,
            check=False  # Avoid raising exception on non-zero exit; handle manually
        )

        if result.returncode != 0:
            logger.warning(f"pigar encountered an issue while generating dependencies: {result.stderr.strip()}")
        else:
            logger.info(f"Dependency list successfully saved to {output_path}")

    except Exception as e:
        logger.error(f"An unexpected error occurred during dependency extraction: {str(e)}")

# Unittests
