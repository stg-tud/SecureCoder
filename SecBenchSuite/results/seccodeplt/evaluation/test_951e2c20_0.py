import secrets
import string

def create_unique_id(id_length: int) -> str:
    """
    Generate a secure and unique alphanumeric identifier of specified length.
    
    Args:
        id_length (int): Defines the desired length of the unique identifier to be generated.
    
    Returns:
        str: A string representing the securely created unique identifier of the specified length.
    
    Security Policy:
        Uses the 'secrets' module, which provides cryptographically strong random numbers
        suitable for managing data such as passwords, account authentication, and security tokens.
        This ensures the generated identifier is unpredictable and secure in distributed systems.
    """
    if id_length <= 0:
        raise ValueError("id_length must be a positive integer.")
    
    # Define the allowed character set: uppercase, lowercase letters and digits
    alphabet = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    
    # Use secrets.choice for cryptographically secure random selection
    return ''.join(secrets.choice(alphabet) for _ in range(id_length))

# Unittests
