import string
import secrets

def create_password(size: int) -> str:
    """
    Generate a secure random password of specified length using cryptographically secure PRNG.
    
    Args:
        size (int): The desired length of the generated password. Must be at least 8.
    
    Returns:
        str: A securely generated password containing uppercase letters, lowercase letters,
             digits, and special symbols.
    
    Raises:
        ValueError: If the given size is smaller than 8.
    
    The function uses the 'secrets' module to ensure cryptographic security and unpredictability,
    suitable for use in user authentication systems.
    """
    if size < 8:
        raise ValueError("Password size must be at least 8 characters long for security reasons.")
    
    # Define the character set: uppercase, lowercase, digits, and punctuation
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets.choice for cryptographically secure randomness
    password = ''.join(secrets.choice(characters) for _ in range(size))
    
    return password

# Unittests
