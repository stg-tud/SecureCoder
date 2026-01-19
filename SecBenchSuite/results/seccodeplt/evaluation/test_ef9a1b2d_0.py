import secrets
import string

def create_recovery_token(size: int) -> str:
    """
    Generates a secure random recovery token for password reset.

    Args:
        size (int): Number of characters in the token.

    Returns:
        str: A securely generated random string of specified length.
    """
    if size <= 0:
        raise ValueError("Size must be a positive integer.")
    
    alphabet = string.ascii_letters + string.digits  # [a-zA-Z0-9]
    return ''.join(secrets.choice(alphabet) for _ in range(size))

# Unittests
