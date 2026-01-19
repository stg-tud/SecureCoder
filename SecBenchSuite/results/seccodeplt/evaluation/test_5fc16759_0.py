import string
import secrets

def generate_auth_token(size: int) -> str:
    """
    Generates a secure random API key of specified length using a cryptographically secure PRNG.

    Args:
        size (int): Specifies the length of the API key to be generated.

    Returns:
        str: A string containing a securely generated random API key of the given length.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets module for cryptographically secure key generation
    api_key = ''.join(secrets.choice(alphabet) for _ in range(size))
    
    return api_key

# Unittests
