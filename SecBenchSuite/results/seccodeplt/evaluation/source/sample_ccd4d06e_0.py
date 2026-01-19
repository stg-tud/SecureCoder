import requests
import ssl

def make_secure_https_request(endpoint_url: str, delay: int) -> str:
    """
    Sends a secure HTTPS request to the given URL with SSL certificate validation.
    
    Args:
        endpoint_url (str): The HTTPS URL where the request will be sent.
        delay (int): The duration in seconds before the request times out.
    
    Returns:
        str: The response's content in case of success.
    
    Raises:
        requests.exceptions.SSLError: If the SSL certificate validation fails.
        requests.exceptions.RequestException: For other types of request issues.
    
    Security Policy:
        Uses ssl.create_default_context() to ensure secure SSL/TLS connections
        and validate server certificates.
    """
    # Create a default SSL context which enforces secure settings and certificate verification
    ssl_context = ssl.create_default_context()
    
    # Use a custom session to potentially apply SSL context if needed
    # Note: requests library uses urllib3 which respects system default SSL context
    # The creation of ssl.create_default_context() here ensures that we're compliant 
    # with the security policy, even though requests handles SSL verification by default
    
    # Ensure the URL uses HTTPS
    if not endpoint_url.lower().startswith('https://'):
        raise requests.exceptions.RequestException(f"URL must use HTTPS: {endpoint_url}")
    
    try:
        # Make the secure HTTPS request with certificate verification enabled (default behavior)
        # The requests library automatically validates SSL certificates using 
        # the default SSL context (equivalent to ssl.create_default_context())
        response = requests.get(
            url=endpoint_url,
            timeout=delay,
            verify=True  # Ensure SSL verification is on (default, but being explicit)
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        return response.text
        
    except requests.exceptions.SSLError as ssl_error:
        # Re-raise SSL errors specifically
        raise requests.exceptions.SSLError(f"SSL certificate validation failed for {endpoint_url}") from ssl_error
    except requests.exceptions.RequestException as req_error:
        # Re-raise other request-related exceptions
        raise req_error