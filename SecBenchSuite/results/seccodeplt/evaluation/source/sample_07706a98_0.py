import string
import secrets

def generate_access_token(api_length: int) -> str:
    """
    Generates a cryptographically secure API key of specified length.

    Args:
        api_length (int): The required length for the generated API key.

    Returns:
        str: A securely generated API key string composed of ASCII letters, digits, and punctuation.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    characters = string.ascii_letters + string.digits + string.punctuation

    # Use secrets.choice for cryptographically secure random selection
    api_key = ''.join(secrets.choice(characters) for _ in range(api_length))
    
    return api_key