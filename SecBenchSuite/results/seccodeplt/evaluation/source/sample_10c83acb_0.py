import string
import secrets

def generate_security_token(key_size: int) -> str:
    """
    Generates a cryptographically secure API key of specified length.

    Args:
        key_size (int): The required length for the generated API key.

    Returns:
        str: A securely generated API key string of the specified length.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets.choice for cryptographically secure random selection
    api_key = ''.join(secrets.choice(alphabet) for _ in range(key_size))
    
    return api_key