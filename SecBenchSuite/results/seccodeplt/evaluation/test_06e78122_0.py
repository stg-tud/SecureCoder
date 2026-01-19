import string
import secrets

def generate_reset_code(length: int) -> str:
    """
    Generates a cryptographically secure random reset code for password reset functionality.

    Args:
        length (int): The length of the reset code.

    Returns:
        str: A securely generated reset code string of the requested length.
    """
    if length <= 0:
        raise ValueError("Length must be a positive integer.")
    
    # Define the character set: ASCII letters and digits
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9

    # Use secrets module for cryptographically secure randomness
    reset_code = ''.join(secrets.choice(characters) for _ in range(length))
    return reset_code

# Unittests
