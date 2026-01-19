import redis
import ssl

def secure_redis_ssl_connect(redis_host: str, redis_port: int, redis_password: str = None, redis_db: int = 0) -> bool:
    """
    Securely connects to a Redis server using SSL/TLS, authenticates if needed, and pings the server.

    Args:
        redis_host (str): The IP or address of the Redis server.
        redis_port (int): The connection port for the Redis service.
        redis_password (str, optional): Password for server authentication when needed.
        redis_db (int, optional): The Redis database index to select.

    Returns:
        bool: True if the ping operation is successful; otherwise False.

    Raises:
        redis.exceptions.ConnectionError: If there are connection issues.
        ssl.SSLError: If there are SSL/TLS certificate validation problems.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()

    try:
        # Establish a secure Redis connection using SSL
        client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
            ssl=True,
            ssl_context=ssl_context,
            socket_connect_timeout=10,
            socket_timeout=10,
            retry_on_timeout=False
        )

        # Send a ping to verify the connection
        return client.ping()

    except (redis.exceptions.ConnectionError, ssl.SSLError):
        # Re-raise ConnectionError and SSLError as specified
        raise
    except Exception:
        # Any other failure (e.g., ping returns False) results in False
        return False

# Unittests
