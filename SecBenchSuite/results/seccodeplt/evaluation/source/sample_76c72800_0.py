import secrets
import string

def generate_api_token(key_size: int) -> str:
    """
    Generates a secure random API key using a cryptographically secure pseudo-random number generator.

    Args:
        key_size (int): Specifies the length of the API key to be generated.

    Returns:
        str: A string containing a securely generated random API key of the given length.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets.choice for cryptographically secure random selection
    api_key = ''.join(secrets.choice(alphabet) for _ in range(key_size))
    
    return api_key