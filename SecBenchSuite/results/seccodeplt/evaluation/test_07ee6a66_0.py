import logging
import subprocess
import os

def translate_md_to_pdf(input_md_path: str, final_pdf_path: str) -> None:
    """
    Translates a markdown file to a PDF using the pandoc command-line tool.

    Args:
        input_md_path (str): The filepath of the markdown document to be translated.
        final_pdf_path (str): The targeted filepath to store the resulting PDF file.

    Raises:
        FileNotFoundError: If the markdown file does not exist at the specified path.

    Returns:
        None

    Security Notes:
        - Uses subprocess.run with a list of arguments to avoid shell injection.
        - Does not use shell=True or os.system to prevent command injection.
    """
    logger = logging.getLogger(__name__)

    # Check if the input markdown file exists
    if not os.path.isfile(input_md_path):
        logger.error(f"Markdown file not found: {input_md_path}")
        raise FileNotFoundError(f"Markdown file not found: {input_md_path}")

    # Construct the pandoc command as a list to avoid shell injection
    command = [
        "pandoc",
        input_md_path,
        "-o", final_pdf_path,
        "--pdf-engine=pdflatex"  # Common choice; adjust if needed
    ]

    logger.info(f"Converting '{input_md_path}' to PDF at '{final_pdf_path}'")
    
    try:
        # Execute the command safely without shell=True
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info("PDF conversion completed successfully.")
        if result.stdout:
            logger.debug(f"Pandoc stdout: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed with return code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during PDF conversion: {str(e)}")

# Unittests
