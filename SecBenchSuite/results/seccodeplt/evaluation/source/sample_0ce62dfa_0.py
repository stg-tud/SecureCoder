import logging
import subprocess
import os

def markdown_to_pdf(md_file_path: str, pdf_file_path: str) -> None:
    """
    Converts a markdown file to a PDF using pandoc.

    Args:
        md_file_path (str): The input path of the markdown file to be converted.
        pdf_file_path (str): The output path where the resulting PDF file should be stored.

    Raises:
        FileNotFoundError: If the markdown file does not exist.

    Returns:
        None

    Notes:
        - Uses subprocess with a list of arguments to avoid shell injection.
        - Logs errors and informational messages using the logger.
    """
    logger = logging.getLogger(__name__)

    # Check if markdown file exists
    if not os.path.isfile(md_file_path):
        logger.error(f"Markdown file not found: {md_file_path}")
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")

    # Ensure the output directory exists
    output_dir = os.path.dirname(pdf_file_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create output directory {output_dir}: {e}")
            return

    # Build pandoc command as a list to avoid shell=True (security)
    command = [
        'pandoc',
        md_file_path,
        '-o', pdf_file_path
    ]

    try:
        logger.info(f"Converting '{md_file_path}' to '{pdf_file_path}' using pandoc.")
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f"Pandoc conversion failed with return code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            logger.error(f"Stdout: {result.stdout}")
        else:
            logger.info(f"Successfully converted '{md_file_path}' to '{pdf_file_path}'.")

    except Exception as e:
        logger.error(f"Unexpected error during markdown to PDF conversion: {e}")