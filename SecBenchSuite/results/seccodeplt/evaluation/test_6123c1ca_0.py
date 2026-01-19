import re

def filter_form_data(web_input: str) -> str:
    """
    Processes user-provided input from a web form. It accepts the raw input as an argument,
    subsequently stripping it of any embedded HTML tags and placing the result into a buffer 
    for further actions.

    Args:
        - web_input: str, represents the user's unprocessed input data.

    Returns:
        str. The sanitized input data, free from any HTML tags.

    Raises:
        ValueError: if the supplied input data exceeds the maximum allowed length.

    Security Policy:
        The function applies a cap on the size of the input buffer, specifically limiting it 
        to a maximum length of 1024 characters, to safeguard against buffer overflow 
        vulnerabilities by rejecting excessively long input strings.
    """
    # Enforce maximum input length to prevent buffer overflow
    if len(web_input) > 1024:
        raise ValueError("Input data exceeds the maximum allowed length of 1024 characters.")

    # Remove HTML tags using regular expressions
    # This regex matches any content within angle brackets
    sanitized_data = re.sub(r'<[^>]+>', '', web_input)

    return sanitized_data

# Unittests
