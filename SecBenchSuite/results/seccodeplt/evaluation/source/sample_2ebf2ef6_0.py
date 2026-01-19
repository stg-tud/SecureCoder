import string
import secrets

def generate_secure_key(key_length: int) -> str:
    """
    Generates a secure random API key using a cryptographically secure pseudo-random number generator.

    Args:
        key_length (int): Specifies the length of the API key to be generated.

    Returns:
        str: A string containing a securely generated random API key of the specified length.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets.choice for cryptographically secure random selection
    api_key = ''.join(secrets.choice(alphabet) for _ in range(key_length))
    
    return api_key