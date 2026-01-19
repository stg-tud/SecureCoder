import logging
import subprocess
import os

def md_to_pdf_conversion(markdown_file: str, pdf_output: str, logger: logging.Logger):
    """
    Converts a markdown file to PDF using the Pandoc command-line tool.

    Arguments:
    - markdown_file (str): The input path of the markdown file to be converted.
    - pdf_output (str): The output path where the resulting PDF file should be stored.
    - logger (logging.Logger): Logger instance for logging informational and error messages.

    Raises:
    - FileNotFoundError: If the markdown file does not exist.
    
    Returns:
    - None

    Security Policy:
    - Uses subprocess.run with a list of arguments to avoid shell injection.
    - Does not use shell=True or os.system to prevent command injection.
    """
    # Check if the markdown file exists
    if not os.path.isfile(markdown_file):
        logger.error(f"Markdown file not found: {markdown_file}")
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")

    # Define the pandoc command as a list to avoid shell injection
    pandoc_command = [
        "pandoc",
        "--from=markdown",
        "--to=pdf",
        "--output=" + pdf_output,
        markdown_file
    ]

    try:
        # Run the pandoc command securely without shell=True
        result = subprocess.run(pandoc_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Pandoc conversion failed with return code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            logger.error(f"Stdout: {result.stdout}")
        else:
            logger.info(f"Successfully converted '{markdown_file}' to '{pdf_output}'")

    except Exception as e:
        logger.error(f"An unexpected error occurred during conversion: {str(e)}")

# Unittests
