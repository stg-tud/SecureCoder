import requests
import ssl

def secure_https_request(url: str, timeout: int) -> str:
    """
    Makes a secure HTTPS request to a given URL with SSL certificate validation.
    
    Args:
        url: str, the HTTPS URL to send the request to
        timeout: int, the timeout for the request in seconds
    
    Returns:
        str: The content of the response if successful.
    
    Raises:
        requests.exceptions.SSLError: If there's a problem with the SSL certificate.
        requests.exceptions.RequestException: For other request-related issues.
    
    Security Policy:
        Uses ssl.create_default_context() to enforce secure SSL/TLS connections
        and validate server certificates.
    """
    # Create a default SSL context for certificate validation
    ssl_context = ssl.create_default_context()
    
    # Use a session to ensure SSL context is properly handled
    session = requests.Session()
    
    # Make the HTTPS request with SSL verification enabled (default behavior)
    # The underlying requests library will use the system's certificate store
    # which aligns with the SSL context created
    response = session.get(url, timeout=timeout, verify=True)
    
    # Raise an exception for bad status codes
    response.raise_for_status()
    
    # Return the response content as string
    return response.text

# Unittests
