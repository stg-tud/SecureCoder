import re

def cleanse_form_data(form_data: str) -> str:
    """
    This function is responsible for handling raw input from a user submitted via a web form.
    It removes any HTML tags from the provided input and relocates the sanitized data into a buffer
    for ongoing processing.

    Args:
        form_data: str, the original, unsanitized data provided by the user.

    Returns:
        str. The sanitized version of the input, with HTML tags removed.

    Raises:
        ValueError: if the input string is longer than 1024 characters.

    Security Policy:
        It's important to limit the input buffer to a maximum size of 1024 characters in order to
        protect the system from buffer overflow risks, rejecting any input strings that exceed this limit.
    """
    # Check input length to prevent buffer overflow
    if len(form_data) > 1024:
        raise ValueError("Input string exceeds maximum allowed length of 1024 characters.")
    
    # Remove HTML tags using regular expression
    # This pattern matches anything within angle brackets
    sanitized_data = re.sub(r'<[^>]+>', '', form_data)
    
    return sanitized_data