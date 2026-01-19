import logging
from pathlib import Path

def gather_dependencies(output_path: str) -> None:
    """
    Retrieves all dependencies for a project and stores them in a specified requirements file.
    Uses the 'pigar' library to scan the project's code and generate the list of dependencies.

    Args:
        output_path (str): The file path where the generated list of dependencies will be saved.

    Raises:
        ModuleNotFoundError: If 'pigar' is not available.

    Returns:
        None

    Note:
        Any errors during dependency capture (other than missing pigar) are logged but not raised.
    """
    logger = logging.getLogger(__name__)

    try:
        import pigar
    except ModuleNotFoundError:
        logger.error("The 'pigar' library is required to gather dependencies but is not installed.")
        raise

    try:
        # Initialize pigar's main controller
        from pigar._vendor.pigar.generate import Generate

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Use pigar's Generate class safely without shell commands
        generator = Generate(
            project_root='.',           # Analyze current directory
            output=str(output_file),
            imports=None,               # Detect all imports
            verbose=False,
            timeout=None,
        )
        generator.run()

        logger.info(f"Dependency list successfully written to {output_path}")

    except Exception as e:
        logger.error(f"Failed to gather dependencies: {str(e)}")

# Unittests
