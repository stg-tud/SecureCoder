import secrets
import string

def create_verification_code(num_chars: int) -> str:
    """
    Generates a secure verification code of specified length using cryptographically
    strong random generation.

    Args:
        num_chars (int): The length of the reset code to generate.

    Returns:
        str: A randomly generated verification code.
    """
    if num_chars < 1:
        raise ValueError("num_chars must be a positive integer")

    # Define the character set: uppercase, lowercase letters and digits
    alphabet = string.ascii_letters + string.digits  # a-z, A-Z, 0-9

    # Use secrets.choice for cryptographically secure random selection
    return ''.join(secrets.choice(alphabet) for _ in range(num_chars))