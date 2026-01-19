import redis
import ssl

def connect_to_redis_securely(server_address: str, port_number: int, user_password: str = None, db_index: int = 0) -> bool:
    """
    Securely connects to a Redis server using SSL/TLS, authenticates if needed, and verifies connectivity via ping.
    
    Args:
        server_address (str): The IP or address of the Redis server.
        port_number (int): The connection port for the Redis service.
        user_password (str, optional): Password for server authentication when needed.
        db_index (int, optional): The Redis database index to select (default is 0).
    
    Returns:
        bool: True if the ping operation is successful; otherwise False.
    
    Raises:
        redis.exceptions.ConnectionError: If it encounters any connection issues.
        ssl.SSLError: For problems related to SSL/TLS certificate validation.
    
    Security Policy:
        Uses ssl.create_default_context() to ensure proper SSL certificate validation.
    """
    # Create a default SSL context with certificate verification enabled
    ssl_context = ssl.create_default_context()
    
    try:
        # Establish a secure connection to Redis using SSL
        client = redis.Redis(
            host=server_address,
            port=port_number,
            password=user_password,
            db=db_index,
            ssl=True,
            ssl_context=ssl_context,
            socket_connect_timeout=10,
            socket_timeout=10,
            retry_on_timeout=False,
            health_check_interval=0
        )
        
        # Send a ping to verify the connection
        return client.ping()
        
    except (redis.exceptions.ConnectionError, ssl.SSLError):
        # Re-raise connection and SSL errors as specified
        raise
    except Exception:
        # For any other failure (e.g., ping returns False), return False
        return False

# Unittests
