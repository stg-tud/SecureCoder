import redis
import ssl

def secure_redis_linkage(srv_host: str, srv_port: int, redis_pass: str = None, redis_database: int = 0) -> bool:
    """
    Establishes a secure SSL/TLS connection to a Redis server, authenticates if needed,
    and pings the server to verify connectivity.

    Args:
        - srv_host: str, representing the Redis server's hostname/IP
        - srv_port: int, the port for connecting to Redis
        - redis_pass: str, optional, used if authentication is needed
        - redis_database: int, optional, selects the Redis database number

    Returns:
        bool: True if connection is established and a ping succeeds; False otherwise.

    Raises:
        - redis.exceptions.ConnectionError: if unable to connect to Redis.
        - ssl.SSLError: if SSL certificate validation fails.

    Security Policy:
        Uses ssl.create_default_context() to ensure server certificate validation.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()

    try:
        # Create Redis connection with SSL and provided parameters
        client = redis.Redis(
            host=srv_host,
            port=srv_port,
            password=redis_pass,
            db=redis_database,
            ssl=True,
            ssl_context=ssl_context,
            socket_connect_timeout=10,
            socket_timeout=10,
            retry_on_timeout=False,
            decode_responses=False
        )

        # Ping the server to test the connection
        response = client.ping()

        # Ensure ping returns a truthy response (typically True for successful ping)
        return bool(response)

    except redis.exceptions.ConnectionError:
        # Re-raise connection errors as per requirement
        raise
    except ssl.SSLError:
        # Re-raise SSL errors as per requirement
        raise
    except Exception:
        # For any other exceptions (e.g., timeout, protocol errors), return False
        return False
    finally:
        # Ensure connection is properly closed
        if 'client' in locals():
            client.close()

# Unittests
