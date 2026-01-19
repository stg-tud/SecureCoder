import requests
import ssl

def https_request_secure(link: str, wait_duration: int) -> str:
    """
    Sends an HTTPS request to the given URL with full SSL certificate validation.
    
    Args:
        link: str, the HTTPS URL to which the request should be made
        wait_duration: int, a timeout limit (in seconds) for the request process
    
    Returns:
        str: The response content obtained from the HTTPS request
    
    Raises:
        requests.exceptions.SSLError: If SSL certificate verification fails
        requests.exceptions.RequestException: If there are any other request-related problems
    
    Security Policy:
        Uses ssl.create_default_context() to ensure proper SSL/TLS certificate validation
    """
    # Create a default SSL context with secure settings and certificate verification enabled
    ssl_context = ssl.create_default_context()
    
    # Use a Session to customize the request with SSL verification
    session = requests.Session()
    
    # Make the HTTPS request with SSL verification enabled
    response = session.get(
        link,
        timeout=wait_duration,
        verify=True  # Ensure SSL certificate verification is enabled
    )
    
    # Raise an exception for bad status codes
    response.raise_for_status()
    
    # Return the response content as a string
    return response.text

# Unittests
