import hashlib


def hash_certificate(cert: str) -> str:
    """
    Hash the given certificate securely and return the hash as a hexadecimal string.

    Args:
        cert (str): The certificate to be hashed.

    Returns:
        str: The securely hashed certificate as a hexadecimal string.
    """
    # Create a new SHA-256 hash object
    hash_object = hashlib.sha256()
    
    # Update the hash object with the bytes of the certificate
    hash_object.update(cert.encode('utf-8'))
    
    # Return the hexadecimal digest of the hash
    return hash_object.hexdigest()