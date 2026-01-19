import secrets
import string

def generate_unique_identifier(length: int) -> str:
    """
    Generate a cryptographically secure, unique identifier consisting of alphanumeric characters.

    Args:
        length (int): The desired length of the identifier.

    Returns:
        str: A securely generated unique identifier string of the specified length.
    """
    if length <= 0:
        return ""

    alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Unittests
