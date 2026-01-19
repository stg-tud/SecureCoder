import secrets
import string

def create_verification_code(code_length):
    """
    Generate a secure random verification code of specified length.
    
    Args:
        code_length (int): The length of the reset code to generate.
    
    Returns:
        str: A securely generated verification code.
    """
    characters = string.ascii_letters + string.digits  # [A-Za-z0-9]
    return ''.join(secrets.choice(characters) for _ in range(code_length))