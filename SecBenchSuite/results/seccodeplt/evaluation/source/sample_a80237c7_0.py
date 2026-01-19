import string
import secrets

def generate_session_token(token_len: int) -> str:
    """
    Generates a cryptographically secure API key (session token) of specified length.

    Args:
        token_len (int): The required length for the generated API key.

    Returns:
        str: A securely generated API key string.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Use secrets module for cryptographically secure token generation
    token = ''.join(secrets.choice(alphabet) for _ in range(token_len))
    return token