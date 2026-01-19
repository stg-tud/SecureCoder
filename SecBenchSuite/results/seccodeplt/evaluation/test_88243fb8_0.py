import string
import secrets

def build_secure_id(char_count: int) -> str:
    """
    Generates a secure, unique identifier of specified length using cryptographically
    secure random generation.

    Args:
        char_count (int): The length of the generated identifier.

    Returns:
        str: A securely generated alphanumeric identifier.
    """
    if char_count < 1:
        raise ValueError("char_count must be a positive integer.")

    # Define the alphabet: uppercase, lowercase letters and digits
    alphabet = string.ascii_letters + string.digits  # a-zA-Z0-9

    # Use secrets.choice for cryptographically secure random selection
    return ''.join(secrets.choice(alphabet) for _ in range(char_count))

# Unittests
