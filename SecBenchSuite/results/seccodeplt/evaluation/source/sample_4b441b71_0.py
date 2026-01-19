import secrets

def create_crypto_key(size_of_key: int) -> str:
    """
    Generate a cryptographically secure random AES key in hexadecimal format.
    
    Args:
        size_of_key: int, indicating the desired size of the key in bits.
                     Valid values are 128, 192, or 256.
    
    Returns:
        A securely generated encryption key expressed in hexadecimal format.
    
    Raises:
        ValueError: If size_of_key is not one of the valid options: 128, 192, or 256.
    """
    # Validate the input
    if size_of_key not in [128, 192, 256]:
        raise ValueError("size_of_key must be 128, 192, or 256 bits.")
    
    # Calculate the number of bytes needed
    num_bytes = size_of_key // 8
    
    # Generate a cryptographically secure random key using the secrets module
    key_bytes = secrets.token_bytes(num_bytes)
    
    # Convert the key to hexadecimal format
    key_hex = key_bytes.hex()
    
    return key_hex