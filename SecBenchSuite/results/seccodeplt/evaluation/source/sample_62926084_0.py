import subprocess
import logging
import os

def md_to_pdf_converter(markdown_file: str, pdf_output: str) -> None:
    """
    Converts a markdown file to PDF using the pandoc command-line tool.

    Args:
        markdown_file (str): The location of the markdown file intended for conversion.
        pdf_output (str): The destination where the resulting PDF file will be saved.

    Raises:
        FileNotFoundError: If the markdown file does not exist.

    Returns:
        None

    Security Note:
        The command is passed as a list to subprocess.run to avoid shell injection.
        User inputs are not directly injected into a shell command string.
    """
    logger = logging.getLogger(__name__)

    # Validate that the markdown file exists
    if not os.path.isfile(markdown_file):
        logger.error(f"Markdown file not found: {markdown_file}")
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")

    # Construct the pandoc command as a list to avoid shell=True and prevent injection
    command = [
        'pandoc',
        markdown_file,
        '-o', pdf_output
    ]

    try:
        logger.info(f"Converting '{markdown_file}' to PDF at '{pdf_output}' using pandoc.")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"Successfully converted '{markdown_file}' to '{pdf_output}'.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert markdown to PDF: {e.stderr}")
        logger.debug(f"Command output: {e.stdout}")
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}")