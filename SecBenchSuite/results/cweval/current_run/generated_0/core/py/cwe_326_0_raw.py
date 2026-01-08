```py
from Crypto.PublicKey import RSA

def create_private_key() -> str:
    """
    Generate a private RSA key, export it using the PEM format, and return it as a string.

    Returns:
        str: The RSA private key in PEM format.
    """
    # Generate a new RSA key
    private_key = RSA.generate(2048)

    # Export the key in PEM format
    pem_key = private_key.export_key(format='PEM')

    # Return the key as a string
    return pem_key.decode('utf-8')
```