import secrets

def generate_encryption_key(key_size: int) -> str:
    """
    Generates a secure random AES encryption key as a hexadecimal string.
    
    Args:
        key_size (int): The size of the key in bits (128, 192, or 256)
    
    Returns:
        str: A securely generated encryption key as a hexadecimal string
    
    Raises:
        ValueError: If key_size is not one of 128, 192, or 256
    """
    if key_size not in [128, 192, 256]:
        raise ValueError("key_size must be 128, 192, or 256")
    
    # Convert bits to bytes
    num_bytes = key_size // 8
    
    # Generate random bytes using cryptographically secure PRNG
    key_bytes = secrets.token_bytes(num_bytes)
    
    # Convert to hexadecimal string
    key_hex = key_bytes.hex()
    
    return key_hex

# Unittests
