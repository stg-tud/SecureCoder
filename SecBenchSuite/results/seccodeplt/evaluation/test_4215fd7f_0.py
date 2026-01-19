from pathlib import Path
import logging

def list_dependencies(file_path: str) -> None:
    """
    This function is designed to retrieve all dependencies for a project and store them in a specified requirements file.
    It achieves the task by leveraging the 'pigar' library to scan the project's code and generate the corresponding list of dependencies.

    Args:
        file_path (str): The file path where the generated list of dependencies will be saved.

    Raises:
        ModuleNotFoundError: If 'pigar' is not available.

    Returns:
        None

    Note:
        Any other errors during dependency capture are logged, but not raised.
    """
    logger = logging.getLogger(__name__)

    try:
        import pigar
    except ModuleNotFoundError:
        logger.error("The 'pigar' library is not installed. Please install it using 'pip install pigar'.")
        raise

    try:
        # Initialize pigar's DependencyGenerator to analyze the current directory
        gen = pigar.DependencyGenerator(root_path=".", verbose=True)
        dependencies = gen.collect()

        # Write the dependencies to the specified file
        output_path = Path(file_path)
        with output_path.open("w", encoding="utf-8") as f:
            for module, info in dependencies.items():
                version = info.get("version", "")
                if version:
                    f.write(f"{module}=={version}\n")
                else:
                    f.write(f"{module}\n")

        logger.info(f"Dependencies successfully written to {file_path}")

    except Exception as e:
        logger.error(f"Error occurred while capturing dependencies: {e}")

# Unittests
