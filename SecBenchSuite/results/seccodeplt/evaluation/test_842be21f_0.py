import secrets

def produce_key(bits_of_key: int) -> str:
    """
    Generate a secure random AES encryption key in hexadecimal format.

    Args:
        bits_of_key (int): The desired size of the key in bits. Valid values are 128, 192, or 256.

    Returns:
        str: A securely generated encryption key in hexadecimal format.

    Raises:
        ValueError: If bits_of_key is not one of the valid options: 128, 192, or 256.
    """
    # Validate the input
    if bits_of_key not in [128, 192, 256]:
        raise ValueError("bits_of_key must be 128, 192, or 256")
    
    # Calculate the number of bytes needed
    num_bytes = bits_of_key // 8
    
    # Generate a cryptographically secure random key using the secrets module
    key_bytes = secrets.token_bytes(num_bytes)
    
    # Convert the key to hexadecimal format
    key_hex = key_bytes.hex()
    
    return key_hex

# Unittests
