import secrets

def generate_secure_key(bits: int) -> str:
    """
    Generate a cryptographically secure AES encryption key as a hexadecimal string.
    
    Args:
        bits (int): Length of the key in bits. Must be one of 128, 192, or 256.
    
    Returns:
        str: A hexadecimal representation of the generated key.
    
    Raises:
        ValueError: If bits is not one of 128, 192, or 256.
    """
    if bits not in (128, 192, 256):
        raise ValueError("bits must be one of 128, 192, or 256")
    
    # Calculate the number of bytes needed
    num_bytes = bits // 8
    
    # Generate cryptographically secure random bytes
    key_bytes = secrets.token_bytes(num_bytes)
    
    # Convert to hexadecimal string
    return key_bytes.hex()

# Unittests
