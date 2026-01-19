import secrets
import string

def build_secure_token(length_of_token: int) -> str:
    """
    Generates a securely random API key of the specified length using a cryptographically 
    secure pseudo-random number generator (PRNG) from the 'secrets' module.

    Args:
        length_of_token (int): The desired length of the API key.

    Returns:
        str: A securely generated random string representing the API key.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets.choice for cryptographically secure random selection
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length_of_token))
    
    return api_key