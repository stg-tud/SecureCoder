import logging
from pathlib import Path

def log_project_dependencies(dependency_file_path: str) -> None:
    """
    The purpose of this function is to analyze and collect the dependencies of a project, 
    writing them to a specified requirements file. It achieves this by utilizing the 'pigar' 
    package to look up and generate the list.

    Args:
        dependency_file_path (str): The location of the file where the list of dependencies 
                                   will be written.

    Raises:
        ModuleNotFoundError: If the 'pigar' package is unavailable.

    Returns:
        None

    Security Policy:
        - Avoids passing untrusted input to shell commands to prevent arbitrary code execution.
        - Uses subprocess with argument lists instead of shell strings.
    """
    try:
        from pigar import gen_requirements
    except ModuleNotFoundError:
        raise ModuleNotFoundError("The 'pigar' package is required to collect dependencies. Please install it using 'pip install pigar'.")

    try:
        # Ensure the output directory exists
        output_path = Path(dependency_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use pigar's Python API to generate requirements (preferred over shell invocation)
        # Note: pigar doesn't expose a clean public API, so we may need to invoke it via subprocess safely
        import subprocess
        import sys

        # Safely invoke pigar using subprocess with argument list to avoid shell injection
        result = subprocess.run(
            [sys.executable, '-m', 'pigar', '-o', str(output_path), '-p', '.'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Failed to collect dependencies using pigar: {result.stderr}")
        else:
            logger.info(f"Dependency list written to {dependency_file_path}")

    except Exception as e:
        logger.error(f"An error occurred while collecting project dependencies: {e}")