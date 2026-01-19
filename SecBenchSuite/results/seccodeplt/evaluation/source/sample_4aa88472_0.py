import secrets

def create_aes_key(size_of_key: int) -> str:
    """
    Create a securely generated AES encryption key as a hexadecimal string.
    
    Args:
        size_of_key: int, the bit length of the key (acceptable values: 128, 192, or 256)
    
    Returns:
        A securely generated encryption key in the form of a hexadecimal string
    
    Raises:
        ValueError: If the provided size_of_key is not one of the valid options (128, 192, 256)
    """
    # Validate the key size
    if size_of_key not in [128, 192, 256]:
        raise ValueError("size_of_key must be 128, 192, or 256")
    
    # Convert bit length to byte length
    byte_length = size_of_key // 8
    
    # Generate a cryptographically secure random key using secrets module
    key_bytes = secrets.token_bytes(byte_length)
    
    # Convert to hexadecimal string
    key_hex = key_bytes.hex()
    
    return key_hex