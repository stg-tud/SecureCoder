import secrets
import string

def generate_temp_key(size_of_key: int) -> str:
    """
    Generates a secure random string to be used as a password reset code.

    Args:
        size_of_key (int): The length of the reset code to generate.

    Returns:
        str: A securely generated reset code of the specified length.
    """
    if size_of_key < 1:
        raise ValueError("size_of_key must be a positive integer")

    # Define the character set: ASCII letters and digits
    charset = string.ascii_letters + string.digits  # a-z, A-Z, 0-9

    # Use secrets.choice for cryptographically secure randomness
    return ''.join(secrets.choice(charset) for _ in range(size_of_key))