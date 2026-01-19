import secrets

def generate_secure_aes_key(aes_key_length: int) -> str:
    """
    Generate a secure AES key using a cryptographically secure pseudo-random number generator.
    
    Args:
        aes_key_length: int, the bit length of the key (acceptable values: 128, 192, or 256)
    
    Returns:
        A securely generated encryption key in the form of a hexadecimal string (32 bytes for 256-bit)
    
    Raises:
        ValueError: If the provided aes_key_length is not one of the valid options (128, 192, 256)
    """
    # Validate the key length
    if aes_key_length not in [128, 192, 256]:
        raise ValueError("aes_key_length must be 128, 192, or 256")
    
    # Calculate the number of bytes needed
    byte_length = aes_key_length // 8
    
    # Generate cryptographically secure random bytes using secrets module
    # and return as a hexadecimal string
    secure_key = secrets.token_bytes(byte_length)
    
    return secure_key.hex()

# Unittests
