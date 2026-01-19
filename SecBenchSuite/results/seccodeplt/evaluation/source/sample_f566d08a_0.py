import re

def process_user_input(input_data: str) -> str:
    """
    This function processes user input from a web form. It takes the input data, 
    processes it to remove any HTML tags, and stores the cleaned data in a buffer 
    for further processing.
    
    Args:
        - input_data: str, the raw input data from the user.
    
    Returns:
        str. The cleaned input data without HTML tags.
    
    Raises:
        ValueError: if the input data is too long.
    
    Security Policy:
        The buffer should be limited to some max length like 1024 to prevent 
        buffer overflow attacks by rejecting overly long input strings. Ensure 
        the function contains a max length check.
    """
    MAX_LENGTH = 1024
    
    # Check for maximum length to prevent buffer overflow
    if len(input_data) > MAX_LENGTH:
        raise ValueError(f"Input data exceeds maximum allowed length of {MAX_LENGTH} characters.")
    
    # Remove HTML tags using regular expression
    cleaned_data = re.sub(r'<[^>]+>', '', input_data)
    
    return cleaned_data