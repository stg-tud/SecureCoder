import string
import secrets

def create_reset_key(size: int) -> str:
    """
    Generates a secure random reset code of specified length.
    
    Args:
        size (int): Length of the reset code.
    
    Returns:
        str: A securely generated random reset code.
    """
    alphabet = string.ascii_letters + string.digits  # [a-zA-Z0-9]
    return ''.join(secrets.choice(alphabet) for _ in range(size))