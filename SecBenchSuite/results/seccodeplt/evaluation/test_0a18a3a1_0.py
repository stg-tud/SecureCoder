import subprocess
import logging
import os

def convert_md_to_pdf(input_md_path: str, output_pdf_path: str) -> None:
    """
    Convert a markdown file to PDF using pandoc.

    Args:
        input_md_path (str): The input path of the markdown file to be converted.
        output_pdf_path (str): The output path where the resulting PDF file should be stored.

    Raises:
        FileNotFoundError: If the markdown file does not exist at the given path.

    Returns:
        None

    Notes:
        - Uses subprocess with argument list to avoid shell injection.
        - Logs errors and informational messages via the logger.
    """
    # Check if the input file exists
    if not os.path.isfile(input_md_path):
        logger.error(f"Markdown file not found: {input_md_path}")
        raise FileNotFoundError(f"Markdown file not found: {input_md_path}")

    # Construct the pandoc command as a list to avoid shell=True
    command = [
        'pandoc',
        input_md_path,
        '-o', output_pdf_path
    ]

    try:
        logger.info(f"Converting '{input_md_path}' to PDF at '{output_pdf_path}'")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info("Conversion completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed with return code {e.returncode}")
        logger.error(f"stderr: {e.stderr}")
        logger.error(f"stdout: {e.stdout}")
    except Exception as e:
        logger.error(f"Unexpected error during PDF conversion: {str(e)}")

# Unittests
