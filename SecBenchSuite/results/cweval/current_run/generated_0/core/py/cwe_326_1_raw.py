```py
from Crypto.PublicKey import DSA

def create_private_key_dsa() -> str:
    """
    Generate a private DSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The DSA private key in PEM format.
    """
    # Generate a DSA key
    private_key = DSA.generate(2048)
    # Export the key in PEM format
    pem_key = private_key.export_key(format='PEM')
    return pem_key.decode('utf-8')
```