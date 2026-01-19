import logging
import os
from pathlib import Path

def capture_dependencies(requirements_path: str) -> None:
    """
    Captures project dependencies and writes them to a specified requirements file using 'pigar'.

    Args:
        requirements_path (str): The path to the file where the dependencies should be written.

    Raises:
        ModuleNotFoundError: If 'pigar' is not installed.

    Security Note:
        Uses subprocess.run with a list to avoid shell injection from user-controlled input.
    """
    try:
        import pigar  # noqa: F401 (verify pigar is available)
    except ModuleNotFoundError:
        logger.error("The 'pigar' package is not installed. Please install it using 'pip install pigar'.")
        raise

    requirements_file = Path(requirements_path)
    try:
        # Ensure the parent directory exists
        requirements_file.parent.mkdir(parents=True, exist_ok=True)

        # Use subprocess.run with a command list to avoid shell injection
        from subprocess import run, PIPE

        result = run(
            ['pigar', '-r', str(requirements_file)],  # Command as a list
            stdout=PIPE,
            stderr=PIPE,
            cwd=Path.cwd(),
            text=True,
            timeout=300  # Prevent hanging indefinitely
        )

        if result.returncode != 0:
            logger.error(f"Failed to capture dependencies using 'pigar'. Error: {result.stderr.strip()}")
        else:
            logger.info(f"Dependencies successfully written to {requirements_path}")

    except Exception as e:
        logger.error(f"An unexpected error occurred while capturing dependencies: {str(e)}")

# Unittests
