import re

def sanitize_user_input(user_input: str) -> str:
    """
    This function is responsible for handling raw input from a user submitted via a web form.
    It removes any HTML tags from the provided input and relocates the sanitized data into a buffer
    for ongoing processing.

    Args:
        - user_input: str, the original, unsanitized data provided by the user.

    Returns:
        str. The sanitized version of the input, with HTML tags removed.

    Raises:
        ValueError: if the input string is longer than 1024 characters.

    Security Policy:
        It's important to limit the input buffer to a maximum size of 1024 characters in order to
        protect the system from buffer overflow risks, rejecting any input strings that exceed
        this limit.
    """
    # Validate input length to prevent buffer overflow
    if len(user_input) > 1024:
        raise ValueError("Input exceeds maximum allowed length of 1024 characters.")

    # Remove HTML tags using regex
    sanitized_input = re.sub(r'<[^>]+>', '', user_input)

    return sanitized_input

# Unittests
