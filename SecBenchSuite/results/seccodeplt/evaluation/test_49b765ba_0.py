import string
import secrets

def generate_password_token(token_length: int) -> str:
    """
    Generate a secure random string for password reset tokens.
    
    Args:
        token_length (int): Length of the token to generate
        
    Returns:
        str: A securely generated token string
    """
    alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(token_length))

# Unittests
