import string
import secrets

def create_password(size: int) -> str:
    """
    Generates a cryptographically secure random password of the specified length.
    
    The password contains a mix of uppercase letters, lowercase letters, digits, 
    and special characters (punctuation) to ensure high entropy and security.
    
    Args:
        size (int): The length of the password to generate. Must be at least 8.
    
    Returns:
        str: A secure random password of the given length.
    
    Raises:
        ValueError: If the provided size is less than 8 characters.
    """
    if size < 8:
        raise ValueError("Password length must be at least 8 characters for security reasons.")
    
    # Define the full character set: uppercase, lowercase, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets module for cryptographically secure randomness
    password = ''.join(secrets.choice(alphabet) for _ in range(size))
    
    return password