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
    # Create an Argon2 hasher instance
    hasher = argon2.PasswordHasher()
    # Hash the password using Argon2
    hash_value = hasher.hash(password)
    return hash_value
```