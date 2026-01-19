import secrets
import string

def generate_auth_token(token_length: int) -> str:
    """
    Generate a secure random API key of specified length using a cryptographically secure PRNG.

    Args:
        token_length (int): The desired length of the API key.

    Returns:
        str: A securely generated random string representing the API key.
    """
    # Define the character set: ASCII letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets.choice for cryptographically secure random selection
    token = ''.join(secrets.choice(alphabet) for _ in range(token_length))
    
    return token

# Unittests
