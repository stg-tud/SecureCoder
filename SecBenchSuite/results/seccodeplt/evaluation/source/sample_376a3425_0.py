import string
import secrets

def create_reset_key(size: int) -> str:
    """
    Generate a securely random reset code of specified length.

    Args:
        size (int): The length of the reset code.

    Returns:
        str: A randomly generated reset code using ASCII letters and digits.
    """
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(secrets.choice(characters) for _ in range(size))