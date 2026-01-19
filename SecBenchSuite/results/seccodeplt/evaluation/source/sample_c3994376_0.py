import string
import secrets

def build_unique_token(token_length: int) -> str:
    """
    Generates a cryptographically secure, unique alphanumeric token of specified length.

    Args:
        token_length (int): The required length of the generated identifier.

    Returns:
        str: A securely generated alphanumeric token.
    """
    if token_length <= 0:
        raise ValueError("token_length must be a positive integer")

    alphabet = string.ascii_letters + string.digits  # Includes a-z, A-Z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(token_length))