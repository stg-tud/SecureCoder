import logging
import subprocess
import os

def convert_markdown_to_pdf_uri(src_markdown_path: str, dest_pdf_path: str) -> None:
    """
    Converts a markdown file to a PDF using the pandoc command-line tool.

    Arguments:
    - src_markdown_path (str): The filepath of the markdown document to be translated.
    - dest_pdf_path (str): The targeted filepath to store the resulting PDF file.

    Context:
    - logger: An instance of logging.Logger for debug and info logging.
    - logging: The built-in Python logging module.
    - subprocess: Used to invoke external commands securely.

    Raises:
    - FileNotFoundError: If the markdown file does not exist at the specified path.

    Returns:
    - None

    Security Policy:
    - Avoid using shell=True or os.system with untrusted input to prevent command injection.
      Instead, pass arguments as a list to subprocess.run.
    """
    logger = logging.getLogger(__name__)

    # Validate that the source markdown file exists
    if not os.path.isfile(src_markdown_path):
        logger.error(f"Markdown file not found: {src_markdown_path}")
        raise FileNotFoundError(f"Markdown file not found: {src_markdown_path}")

    # Construct the pandoc command as a list to avoid shell injection
    command = [
        'pandoc',
        src_markdown_path,
        '-o', dest_pdf_path,
        '--pdf-engine=pdflatex'  # Commonly used PDF engine; adjust if needed
    ]

    logger.info(f"Converting '{src_markdown_path}' to PDF at '{dest_pdf_path}'")
    
    try:
        # Execute pandoc securely without shell=True
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"Pandoc conversion failed with return code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            logger.info(f"Stdout: {result.stdout}")
        else:
            logger.info(f"Successfully generated PDF: {dest_pdf_path}")
            
    except Exception as e:
        logger.error(f"An unexpected error occurred during conversion: {e}")
        raise

# Unittests
