import string
import secrets

def generate_password(length: int) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        length (int): The length of the generated password.

    Returns:
        str: A securely generated password string of the specified length
             containing uppercase, lowercase letters, digits, and punctuation.

    Raises:
        ValueError: If length is less than 8.
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    # Define the character set: uppercase, lowercase, digits, and special characters
    characters = string.ascii_letters + string.digits + string.punctuation

    # Use cryptographically secure secrets module to generate the password
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password

# Unittests
