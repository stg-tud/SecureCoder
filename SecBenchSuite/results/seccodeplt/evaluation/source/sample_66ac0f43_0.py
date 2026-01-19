import logging
import subprocess
import os

def markdown_to_pdf_conversion(md_file_path: str, pdf_file_output: str, logger: logging.Logger):
    """
    Converts a markdown file to PDF using the Pandoc command-line tool.

    Parameters:
        md_file_path (str): The location of the markdown file intended for conversion.
        pdf_file_output (str): The destination where the resulting PDF file will be saved.
        logger (logging.Logger): Logger instance for logging information and errors.

    Raises:
        FileNotFoundError: If the markdown file does not exist at the specified path.

    Returns:
        None

    Security Notes:
        - The command is passed as a list to subprocess.run to prevent shell injection.
        - User-supplied file paths are validated for existence but not blindly trusted.
    """
    # Validate that the markdown file exists
    if not os.path.isfile(md_file_path):
        logger.error(f"Markdown file not found: {md_file_path}")
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")

    # Ensure the output directory exists
    output_dir = os.path.dirname(pdf_file_output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create output directory {output_dir}: {e}")
            return

    # Construct the pandoc command as a list to avoid shell=True and prevent injection
    command = [
        "pandoc",
        md_file_path,
        "-o", pdf_file_output,
        "--pdf-engine=pdflatex"  # Common choice; adjust if needed
    ]

    try:
        logger.info(f"Converting '{md_file_path}' to '{pdf_file_output}' using Pandoc.")
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully converted '{md_file_path}' to '{pdf_file_output}'.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed with return code {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error during PDF conversion: {e}")