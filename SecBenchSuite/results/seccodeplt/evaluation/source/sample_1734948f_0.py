import logging
import subprocess
import os

def convert_md_to_pdf(md_path: str, output_pdf_path: str) -> None:
    """
    Converts a markdown file to a PDF using the pandoc command-line tool.

    Arguments:
    - md_path (str): The filepath of the markdown document to be translated.
    - output_pdf_path (str): The targeted filepath to store the resulting PDF file.

    Raises:
    - FileNotFoundError: If the markdown file does not exist at the specified path.

    Security Policy:
    - Avoids shell injection by using a list of arguments with subprocess.run instead of shell=True.
    """
    logger = logging.getLogger(__name__)

    # Check if the markdown file exists
    if not os.path.isfile(md_path):
        logger.error(f"Markdown file not found: {md_path}")
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # Construct the pandoc command securely using a list to avoid shell injection
    command = [
        "pandoc",
        md_path,
        "-o", output_pdf_path,
        "--pdf-engine=pdflatex"  # Optional: specify PDF engine, can be adjusted
    ]

    logger.info(f"Converting '{md_path}' to PDF at '{output_pdf_path}'")
    
    try:
        # Execute the command safely without shell=True
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info("Conversion completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert markdown to PDF: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}")