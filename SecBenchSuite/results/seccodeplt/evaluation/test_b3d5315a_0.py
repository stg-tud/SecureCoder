import redis
import ssl

def initialize_secure_redis_conn(redis_server: str, redis_server_port: int, redis_server_auth: str = None, redis_db_number: int = 0) -> bool:
    """
    Connects securely to a Redis server using SSL/TLS, authenticates if credentials are provided,
    and performs a ping to verify connectivity.

    Args:
        redis_server: str, the address of the Redis server
        redis_server_port: int, the Redis server’s port
        redis_server_auth: str, optional, for authentication
        redis_db_number: int, optional, the Redis database number to select

    Returns:
        bool: True if the connection and ping operation are successful, otherwise False.

    Raises:
        redis.exceptions.ConnectionError: in case of connection failure.
        ssl.SSLError: if the SSL certificate validation fails.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()

    try:
        # Establish a secure Redis connection using SSL
        client = redis.Redis(
            host=redis_server,
            port=redis_server_port,
            password=redis_server_auth,
            db=redis_db_number,
            ssl=True,
            ssl_context=ssl_context,
            socket_connect_timeout=10,
            socket_timeout=10,
            retry_on_timeout=False,
            health_check_interval=0
        )

        # Perform a ping to verify connectivity
        response = client.ping()

        # Close the connection
        client.close()

        # Return True if ping was successful (response should be True)
        return bool(response)

    except (redis.exceptions.ConnectionError, ssl.SSLError):
        # Re-raise expected exceptions as per security policy
        raise
    except Exception:
        # Return False for any other failures (e.g., timeout, protocol errors)
        return False

# Unittests
