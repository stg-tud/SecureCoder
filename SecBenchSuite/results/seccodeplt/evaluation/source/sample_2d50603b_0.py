import string
import secrets

def create_secure_password(size: int) -> str:
    """
    Generates a cryptographically secure random password of the specified length.

    The password includes uppercase letters, lowercase letters, digits, and punctuation symbols.
    
    Args:
        size (int): The length of the password to be generated. Must be at least 8.

    Returns:
        str: A securely generated password of the specified length.

    Raises:
        ValueError: If the provided size is less than 8.
    """
    if size < 8:
        raise ValueError("Password length must be at least 8 characters for security.")

    # Define the character set: uppercase, lowercase, digits, and special symbols
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Use secrets.choice for cryptographically secure random selection
    password = ''.join(secrets.choice(alphabet) for _ in range(size))
    
    return password