import secrets

def generate_cryptographic_key(length_bits: int) -> str:
    """
    Generate a cryptographically secure AES encryption key as a hexadecimal string.
    
    Args:
        length_bits: int, specifying the length of the key in bits (must be 128, 192, or 256)
    
    Returns:
        A cryptographically secure encryption key as a hexadecimal string
    
    Raises:
        ValueError: If length_bits is not one of 128, 192, or 256
    """
    if length_bits not in (128, 192, 256):
        raise ValueError("length_bits must be one of 128, 192, or 256")
    
    # Convert bit length to bytes (8 bits = 1 byte)
    length_bytes = length_bits // 8
    
    # Generate cryptographically secure random bytes using secrets
    key_bytes = secrets.token_bytes(length_bytes)
    
    # Convert to hexadecimal string
    key_hex = key_bytes.hex()
    
    return key_hex

# Unittests
