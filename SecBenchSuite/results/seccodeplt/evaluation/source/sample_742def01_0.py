import logging
import subprocess
import os

def convert_markdown_to_pdf(markdown_path: str, pdf_path: str) -> None:
    """
    Converts a markdown file to a PDF using an external tool.
    This function leverages the 'pandoc' command-line tool to perform the conversion.

    Args:
        markdown_path (str): The path to the markdown file to be converted.
        pdf_path (str): The path where the output PDF should be saved.

    Raises:
        FileNotFoundError: If the markdown file does not exist.
    
    Returns:
        None

    Note:
        - Logs error messages if the conversion fails, but doesn't raise other exceptions directly.
        - Uses subprocess.run with a command list to avoid shell injection vulnerabilities.
    """
    logger = logging.getLogger(__name__)

    # Check if the markdown file exists
    if not os.path.isfile(markdown_path):
        logger.error(f"Markdown file not found: {markdown_path}")
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    # Construct the pandoc command as a list to avoid shell injection
    command = [
        "pandoc",
        markdown_path,
        "-o", pdf_path,
        "--pdf-engine=pdflatex"
    ]

    try:
        # Execute the command safely without using shell=True
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"Successfully converted {markdown_path} to {pdf_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed with return code {e.returncode}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during PDF conversion: {str(e)}")