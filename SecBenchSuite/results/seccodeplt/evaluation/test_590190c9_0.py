import string
import secrets

def create_secure_token(token_length: int) -> str:
    """
    Create a securely generated random password for user authentication.

    Args:
        token_length: int, the desired length of the generated password.

    Returns:
        A securely generated string password with the specified length that has high randomness.

    Raises:
        ValueError: If the given token_length is smaller than 8.

    The password includes uppercase letters, lowercase letters, digits, and special symbols,
    and is generated using the 'secrets' module for cryptographic security.
    """
    if token_length < 8:
        raise ValueError("token_length must be at least 8 for security reasons.")

    # Define the character set: uppercase, lowercase, digits, and punctuation
    characters = string.ascii_letters + string.digits + string.punctuation

    # Use secrets module to generate a cryptographically secure random password
    token = ''.join(secrets.choice(characters) for _ in range(token_length))
    
    return token

# Unittests
