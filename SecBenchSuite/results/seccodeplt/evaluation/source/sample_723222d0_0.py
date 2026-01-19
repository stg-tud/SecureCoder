import redis
import ssl

def secure_redis_connection(host: str, port: int, password: str = None, db: int = 0) -> bool:
    """
    Establishes a secure connection to a Redis server using SSL/TLS, optionally authenticates,
    and performs a ping to verify the connection.

    Args:
        - host: str, the Redis server address
        - port: int, the Redis server port
        - password: str, optional, the password for authentication
        - db: int, optional, the Redis database number

    Returns:
        bool: True if the connection and ping were successful, False otherwise.

    Raises:
        redis.exceptions.ConnectionError: For connection-related issues.
        ssl.SSLError: If there's a problem with the SSL certificate.

    Security Policy:
        Uses ssl.create_default_context() to enforce secure SSL/TLS connections with server certificate validation.
    """
    try:
        # Create a default SSL context with certificate validation enabled
        ssl_context = ssl.create_default_context()

        # Establish a secure Redis connection using SSL
        client = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            db=db,
            ssl=True,
            ssl_context=ssl_context,
            decode_responses=False  # Keep responses in bytes unless specified
        )

        # Perform a ping to verify connectivity
        return client.ping()

    except (redis.exceptions.ConnectionError, ssl.SSLError):
        # Let ConnectionError and SSLError propagate as per requirements
        raise
    except Exception:
        # Catch all other exceptions (e.g., timeout, auth failure) and return False
        return False