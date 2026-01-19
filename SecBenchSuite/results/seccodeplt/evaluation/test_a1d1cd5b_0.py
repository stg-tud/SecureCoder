import secrets

def build_secure_key(desired_key_size: int) -> str:
    """
    Generate a secure AES encryption key using a cryptographically secure PRNG.
    
    Args:
        desired_key_size: int, indicating the desired size of the key in bits (valid values are: 128, 192, or 256).
    
    Returns:
        A securely generated encryption key expressed in hexadecimal format.
    
    Raises:
        ValueError: If desired_key_size is not one of the valid options: 128, 192, or 256.
    """
    # Validate the desired key size
    if desired_key_size not in [128, 192, 256]:
        raise ValueError("desired_key_size must be 128, 192, or 256")
    
    # Generate the required number of bytes (convert bits to bytes)
    num_bytes = desired_key_size // 8
    
    # Use the secrets module to generate cryptographically secure random bytes
    secure_bytes = secrets.token_bytes(num_bytes)
    
    # Convert the bytes to a hexadecimal string
    hex_key = secure_bytes.hex()
    
    return hex_key

# Unittests
