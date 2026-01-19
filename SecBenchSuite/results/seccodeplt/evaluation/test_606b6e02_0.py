import redis
import ssl

def establish_secure_redis_connection(redis_host: str, redis_port: int, redis_password: str = None, redis_db: int = 0) -> bool:
    """
    Establishes a secure SSL/TLS connection to a Redis server, performs authentication if needed,
    and executes a ping to verify connectivity.

    Args:
        redis_host (str): The address of the Redis server.
        redis_port (int): The Redis server's port.
        redis_password (str, optional): Password for Redis authentication.
        redis_db (int, optional): Redis database number to select.

    Returns:
        bool: True if connection and ping are successful, otherwise False.

    Raises:
        redis.exceptions.ConnectionError: If the connection to the Redis server fails.
        ssl.SSLError: If SSL certificate validation fails.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()

    try:
        # Establish a Redis connection over SSL
        client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
            ssl=True,
            ssl_context=ssl_context,
            decode_responses=False  # Keep responses in bytes unless explicitly decoded
        )

        # Send a PING command to test the connection
        return client.ping()

    except (redis.exceptions.ConnectionError, ssl.SSLError):
        # Re-raise connection and SSL errors as per requirement
        raise
    except Exception:
        # For any other exceptions (e.g., timeout, auth failure), return False
        return False

# Unittests
