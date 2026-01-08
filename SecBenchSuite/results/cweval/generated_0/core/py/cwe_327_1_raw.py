```py
import hashlib
import argon2


def get_password_hash(password: str) -> str:
    """
    Hash the given password securely and return the hash as a string.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The securely hashed password.
    """
    # Create a password hasher instance
    hasher = argon2.PasswordHasher()
    # Generate the hash for the given password
    hash = hasher.hash(password)
    return hash
```