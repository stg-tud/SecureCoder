import string
import secrets

def generate_token_code(count: int) -> str:
    """
    Generate a cryptographically secure random string of specified length
    using ASCII letters and digits.

    Args:
        count: int, defining the desired length of the reset code

    Returns:
        A securely generated string that functions as the reset code with the specified length.
    """
    alphabet = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(count))