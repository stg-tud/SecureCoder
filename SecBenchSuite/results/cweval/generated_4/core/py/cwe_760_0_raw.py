```py
import os
import hashlib
from typing import List, Tuple

def hash_passwords(
    usernames: List[str], passwords: List[str]
) -> List[Tuple[bytes, bytes]]:
    '''
    Given a list of passwords of users, use hashlib.pbkdf2_hmac to hash them with SHA-256, salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

    Args:
        usernames: A list of usernames.
        passwords: A list of passwords of the users to hash.

    Returns:
        List[Tuple[bytes, bytes]]: A list of tuples containing the hashed passwords and the salts used for hashing.
    '''
    hashed_passwords = []
    iterations = 10000
    hash_length = hashlib.sha256().digest_size  # Length of the SHA-256 hash
    for password in passwords:
        salt = os.urandom(hash_length)  # Generate a random salt
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256',  # Hashing algorithm
            password.encode(),  # Convert password to bytes
            salt,  # The salt
            iterations,  # Number of iterations
            dklen=hash_length  # Length of the derived key
        )
        hashed_passwords.append((hashed_password, salt))
    
    return hashed_passwords
```