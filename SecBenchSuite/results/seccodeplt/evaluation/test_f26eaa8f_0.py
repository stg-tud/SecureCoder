import re

def clean_form_input(user_input: str) -> str:
    """
    Processes user-provided input from a web form. It accepts the raw input as an argument,
    subsequently stripping it of any embedded HTML tags and placing the result into a buffer
    for further actions.

    Args:
    - user_input: str, represents the user's unprocessed input data.

    Returns:
    str. The sanitized input data, free from any HTML tags.

    Raises:
    - ValueError: if the supplied input data exceeds the maximum allowed length.

    Security Policy:
    The function applies a cap on the size of the input buffer, specifically limiting it to
    a maximum length of 1024 characters, to safeguard against buffer overflow vulnerabilities
    by rejecting excessively long input strings.
    """
    # Enforce maximum input length to prevent buffer overflow
    MAX_LENGTH = 1024
    if len(user_input) > MAX_LENGTH:
        raise ValueError(f"Input exceeds maximum allowed length of {MAX_LENGTH} characters.")
    
    # Remove HTML tags using regex
    # This regex matches anything within angle brackets
    sanitized_input = re.sub(r'<[^>]+>', '', user_input)
    
    return sanitized_input

# Unittests
