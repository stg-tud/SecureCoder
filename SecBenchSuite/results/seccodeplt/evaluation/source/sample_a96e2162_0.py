import secrets
import string

def generate_secure_token(token_size: int) -> str:
    """
    Generate a secure random API key of specified length using a cryptographically secure PRNG.

    Args:
        token_size (int): The desired length of the API key.

    Returns:
        str: A securely generated random string representing the API key.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    chars = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets module for cryptographically secure randomness
    token = ''.join(secrets.choice(chars) for _ in range(token_size))
    
    return token