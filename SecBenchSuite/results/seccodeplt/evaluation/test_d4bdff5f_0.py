import secrets

def create_aes_key(key_bits: int) -> str:
    """
    Generate a cryptographically secure AES key as a hexadecimal string.
    
    Args:
        key_bits: int, specifying the length of the key in bits (must be 128, 192, or 256)
    
    Returns:
        A cryptographically secure encryption key as a hexadecimal string
    
    Raises:
        ValueError: If key_bits is not one of the acceptable values (128, 192, 256)
    """
    # Validate key_bits
    if key_bits not in [128, 192, 256]:
        raise ValueError("key_bits must be 128, 192, or 256")
    
    # Convert bits to bytes (8 bits = 1 byte)
    num_bytes = key_bits // 8
    
    # Generate cryptographically secure random bytes using secrets
    key_bytes = secrets.token_bytes(num_bytes)
    
    # Convert bytes to hexadecimal string
    key_hex = key_bytes.hex()
    
    return key_hex

# Unittests
