from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using CBC mode.
    The provided key bytes is long enough (>= 64 bytes) for all available algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
    Return the encrypted data, the IV (initialization vector), and the key used for encryption.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the IV, and the key used for encryption.
    '''
    # Use AES for encryption, which requires a key of 16, 24, or 32 bytes.
    # Here we will use a 32-byte key for AES-256.
    aes_key = key[:32]  # Use the first 32 bytes of the provided key.
    
    # Create a new AES cipher in CBC mode.
    cipher = AES.new(aes_key, AES.MODE_CBC)
    
    # Generate a random initialization vector (IV).
    iv = cipher.iv
    
    # Pad the data to be encrypted to ensure it's a multiple of the block size.
    padded_data = pad(data, AES.block_size)
    
    # Encrypt the padded data.
    encrypted_data = cipher.encrypt(padded_data)
    
    return encrypted_data, iv, aes_key