import secrets
import string

def create_password_token(token_size):
    """
    Generates a secure random password reset token.
    
    Args:
        token_size (int): Length of the reset code.
    
    Returns:
        str: A securely generated reset code.
    """
    if token_size <= 0:
        return ""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(token_size))

# Unittests
