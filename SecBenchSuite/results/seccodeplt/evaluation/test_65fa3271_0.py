import requests
import ssl

def send_secure_https_request(link: str, response_timeout: int) -> str:
    """
    Sends a secure HTTPS request to the given URL with SSL certificate validation.

    Args:
        link (str): The HTTPS URL where the request will be sent.
        response_timeout (int): The duration in seconds before the request times out.

    Returns:
        str: The response's content in case of success.

    Raises:
        requests.exceptions.SSLError: If the SSL certificate validation fails.
        requests.exceptions.RequestException: For other types of request issues.
    
    Security Policy:
        Uses ssl.create_default_context() to ensure secure SSL/TLS connections
        with proper certificate verification.
    """
    # Create a default SSL context with secure settings and certificate verification enabled
    ssl_context = ssl.create_default_context()
    
    # Use a custom adapter to apply the SSL context to the requests session
    class SSLAdapter(requests.adapters.HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            kwargs['ssl_context'] = ssl_context
            return super().init_poolmanager(*args, **kwargs)

    # Create a session and mount the adapter for HTTPS requests
    session = requests.Session()
    session.mount('https://', SSLAdapter())
    
    try:
        # Make the secure HTTPS request
        response = session.get(link, timeout=response_timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.SSLError:
        # Propagate SSL errors directly
        raise
    except requests.exceptions.RequestException:
        # Propagate other request-related errors
        raise
    finally:
        # Clean up the session
        session.close()

# Unittests
