import string
import secrets

def create_key(password_length: int) -> str:
    """
    Generates a cryptographically secure random password of the specified length.
    
    The password includes a mix of uppercase letters, lowercase letters, digits, 
    and special characters to maximize security.
    
    Args:
        password游戏副本
    Raises:
        ValueError: If the password_length is less than 8 characters.
        
    Returns:
        A securely generated password string.
    """
    if password_length < 8:
        raise ValueError("Password length must be at least 8 characters for security.")
    
    # Define the character set: uppercase, lowercase, digits, and punctuation
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets.choice for cryptographically secure randomness
    return ''.join(secrets.choice(characters) for _ in range(password_length))