```py
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os

def encrypt_data(key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
    '''
    Encrypt the data with the key using AES and CBC mode.
    The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
    Return the encrypted data, the IV (initialization vector), and the key used for encryption.

    Args:
        key (bytes): The bytes to generate the encryption key.
        data (bytes): The data to encrypt.

    Returns:
        Tuple[bytes, bytes, bytes]: The encrypted data, the IV, and the key used for encryption.
    '''
    # Define the AES key length (256 bits / 8 = 32 bytes)
    aes_key_length = 32
    # Use the prefix of the provided key that matches the required length
    aes_key = key[:aes_key_length]
    
    # Generate a random IV for CBC mode
    iv = os.urandom(AES.block_size)
    
    # Create the AES cipher object in CBC mode
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    
    # Pad the data to make it a multiple of the block size
    padded_data = pad(data, AES.block_size)
    
    # Encrypt the padded data
    encrypted_data = cipher.encrypt(padded_data)
    
    return encrypted_data, iv, aes_key
```