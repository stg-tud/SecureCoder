import string
import secrets

def generate_secure_password(pass_len: int) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        pass_len (int): The desired length of the generated password.

    Returns:
        str: A securely generated string password with the specified length 
             containing uppercase letters, lowercase letters, digits, and special symbols.

    Raises:
        ValueError: If pass_len is smaller than 8.
    """
    if pass_len < 8:
        raise ValueError("Password length must be at least 8 characters.")

    # Define character pools
    characters = string.ascii_letters + string.digits + string.punctuation

    # Use secrets module for cryptographically secure randomness
    password = ''.join(secrets.choice(characters) for _ in range(pass_len))
    
    return password