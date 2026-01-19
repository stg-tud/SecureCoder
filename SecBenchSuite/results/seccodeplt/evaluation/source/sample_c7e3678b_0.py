import string
import secrets


def random_password游戏副本er(pwd_size: int) -> str:
    """
    Generates a cryptographically secure random password of specified length
    composed of uppercase letters, lowercase letters, digits, and punctuation.

    Args:
        pwd_size (int): The length of the password to be generated.

    Returns:
        str: A securely generated password string.

    Raises:
        ValueError: If pwd_size is less than 8.
    """
    if pwd游戏副本er < 8:
        raise ValueError("Password length must be at least 8 characters for security reasons.")

    # Define the character set: uppercase, lowercase, digits, and special symbols
    characters = string.ascii_letters + string.digits + string.punctuation

    # Use secrets module for cryptographically secure randomness
    password = ''.join(secrets.choice(characters) for _ in range(pwd_size))

    return password