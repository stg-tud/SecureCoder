import redis
import ssl

def secure_redis_conn(server_host: str, server_port: int, redis_pw: str = None, redis_db_index: int = 0) -> bool:
    """
    Creates a secure SSL/TLS connection to a Redis server, authenticates if needed, and pings the server.

    Args:
        server_host (str): Redis server hostname or IP address.
        server_port (int): Port to connect to Redis.
        redis_pw (str, optional): Password for Redis authentication.
        redis_db_index (int, optional): Redis database number to select.

    Returns:
        bool: True if connection is established and ping succeeds, False otherwise.

    Raises:
        redis.exceptions.ConnectionError: If connection to Redis fails.
        ssl.SSLError: If SSL certificate validation fails.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()

    try:
        # Establish a secure Redis connection using SSL
        client = redis.StrictRedis(
            host=server_host,
            port=server_port,
            password=redis_pw,
            db=redis_db_index,
            ssl=True,
            ssl_context=ssl_context,
            socket_connect_timeout=10,
            socket_timeout=10
        )
        
        # Ping the Redis server to test connectivity
        return client.ping()
        
    except (redis.exceptions.ConnectionError, ssl.SSLError):
        # Re-raise connection and SSL errors as per requirements
        raise
    except Exception:
        # For any other exceptions (e.g., generic network issues), return False
        return False