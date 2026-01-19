import string
import secrets

def create_api_key(length: int) -> str:
    """
    Generates a secure random API key of the specified length.

    Args:
        length (int): The required length of the API key.

    Returns:
        str: A securely generated random API key.
    """
    if length <= 0:
        raise ValueError("Length must be a positive integer.")
    
    # Define the character set: letters (upper and lower), digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Use secrets.choice for cryptographically secure random selection
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return api_key