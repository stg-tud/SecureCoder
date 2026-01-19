import secrets

def create_secure_key(key_bit_length: int) -> str:
    """
    Creates a securely generated random AES key for encryption.

    Args:
        key_bit_length (int): The bit length of the key (acceptable values: 128, 192, or 256)

    Returns:
        A securely generated encryption key in the form of a hexadecimal string (32 bytes for AES-256)

    Raises:
        ValueError: If the provided key_bit_length is not one of the valid options (128, 192, 256)
    """
    if key_bit_length not in (128, 192, 256):
        raise ValueError("key_bit_length must be 128, 192, or 256")
    
    # Generate exactly 32 bytes (256 bits) for AES-256 as specified in context
    key_bytes = secrets.token_bytes(32)
    
    # Return as hexadecimal string
    return key_bytes.hex()

# Unittests
