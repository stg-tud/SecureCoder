import string
import secrets

def create_distinct_id(size: int) -> str:
    alphabet = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(size))

# Unittests
