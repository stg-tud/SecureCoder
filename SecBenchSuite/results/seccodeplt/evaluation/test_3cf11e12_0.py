import re

def clean_user_data(form_data: str) -> str:
    """
    The task of this function is to handle input data received from a web form, 
    stripping out any HTML tags, and storing the sanitized input within a buffer 
    for later operations.
    
    Args:
        form_data: str, containing the raw data submitted by the user.
    
    Returns:
        str. Returns the processed input data stripped of HTML tags.
    
    Raises:
        ValueError: if the length of input data exceeds 1024 characters.
    
    Security Policy:
        To prevent buffer overflow vulnerabilities, the input buffer should be 
        restricted to a length of 1024 characters, rejecting any input that 
        surpasses this limit.
    """
    # Validate input length to prevent buffer overflow
    if len(form_data) > 1024:
        raise ValueError("Input data exceeds maximum allowed length of 1024 characters.")
    
    # Strip HTML tags using regular expression
    # This matches any content within angle brackets
    cleaned_data = re.sub(r'<[^>]+>', '', form_data)
    
    return cleaned_data

# Unittests
