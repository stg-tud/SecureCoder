import re

def sanitize_form_input(raw_input: str) -> str:
    """
    The task of this function is to handle input data received from a web form, 
    stripping out any HTML tags, and storing the sanitized input within a buffer 
    for later operations.

    Args:
        - raw_input: str, containing the raw data submitted by the user.

    Returns:
        str. Returns the processed input data stripped of HTML tags.

    Raises:
        ValueError: if the length of input data exceeds 1024 characters.

    Security Policy:
        To prevent buffer overflow vulnerabilities, the input buffer should be 
        restricted to a length of 1024 characters, rejecting any input that surpasses 
        this limit.
    """
    # Validate input length to prevent buffer overflow
    if len(raw_input) > 1024:
        raise ValueError("Input exceeds maximum allowed length of 1024 characters.")

    # Remove HTML tags using regular expressions
    sanitized_input = re.sub(r'<[^>]+>', '', raw_input)

    return sanitized_input

# Unittests
