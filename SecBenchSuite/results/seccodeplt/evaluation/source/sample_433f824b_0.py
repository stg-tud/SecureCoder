import redis
import ssl

def create_secure_redis_conn(redis_host_address: str, redis_port_number: int, redis_pass: str = None, redis_db_idx: int = 0) -> bool:
    """
    Connects securely to a Redis server using SSL/TLS, authenticates if needed, and pings the server.

    Args:
        redis_host_address (str): The address of the Redis server.
        redis_port_number (int): The Redis server’s port.
        redis_pass (str, optional): Password for authentication.
        redis_db_idx (int, optional): The Redis database number to select. Defaults to 0.

    Returns:
        bool: True if connection and ping are successful, otherwise False.

    Raises:
        redis.exceptions.ConnectionError: If the connection fails.
        ssl.SSLError: If SSL certificate validation fails.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()

    try:
        # Establish a secure Redis connection using SSL
        client = redis.StrictRedis(
            host=redis_host_address,
            port=redis_port_number,
            password=redis_pass,
            db=redis_db_idx,
            ssl=True,
            ssl_context=ssl_context
        )
        
        # Send a ping to verify the connection
        return client.ping()
    
    except (redis.exceptions.ConnectionError, ssl.SSLError):
        # Re-raise expected exceptions as per requirement
        raise
    except Exception:
        # Return False for any other failure (e.g., timeout, auth failure)
        return False