import logging
import subprocess
import os

def markdown_to_pdf(md_path: str, pdf_dest: str, logger: logging.Logger) -> None:
    """
    Converts a markdown file to PDF using the pandoc command-line tool.

    Args:
        md_path (str): The location of the markdown file intended for conversion.
        pdf_dest (str): The destination where the resulting PDF file will be saved.
        logger (logging.Logger): Logger instance for logging information and errors.

    Raises:
        FileNotFoundError: If the markdown file does not exist.

    Returns:
        None

    Security Note:
        The function uses a list of arguments with subprocess.run to avoid shell injection.
        User inputs are not passed through a shell, mitigating command injection risks.
    """
    # Validate that the markdown file exists
    if not os.path.isfile(md_path):
        logger.error(f"Markdown file not found: {md_path}")
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # Ensure the destination directory exists
    pdf_dir = os.path.dirname(pdf_dest)
    if pdf_dir and not os.path.exists(pdf_dir):
        try:
            os.makedirs(pdf_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create destination directory {pdf_dir}: {e}")
            return

    # Build the command securely as a list to avoid shell injection
    command = [
        "pandoc",
        md_path,
        "-o", pdf_dest,
        "--pdf-engine=pdflatex"  # Common choice; adjust if needed
    ]

    try:
        logger.info(f"Converting '{md_path}' to '{pdf_dest}' using pandoc.")
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            logger.error(f"Pandoc conversion failed with return code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            logger.info(f"stdout: {result.stdout}")
        else:
            logger.info(f"Successfully converted '{md_path}' to '{pdf_dest}'.")

    except Exception as e:
        logger.error(f"Unexpected error during PDF conversion: {e}")

# Unittests
