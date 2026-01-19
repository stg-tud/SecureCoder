import requests
import ssl

def validated_https_query(endpoint_url: str, delay_limit: int) -> str:
    """
    Performs a secure HTTPS request to the specified URL with SSL certificate verification.
    
    Args:
        endpoint_url (str): The HTTPS URL endpoint to which the request will be sent.
        delay_limit (int): Defines the time limit for the request in seconds.
    
    Returns:
        str: The content of the HTTP response upon successful execution.
    
    Raises:
        requests.exceptions.SSLError: When there is an SSL certificate verification issue.
        requests.exceptions.RequestException: For other HTTP request-related problems.
    
    Security Policy:
        Uses ssl.create_default_context() to enforce proper SSL/TLS certificate validation.
    """
    # Create a default SSL context which enforces secure certificate validation
    ssl_context = ssl.create_default_context()
    
    # Use a session to ensure proper SSL context handling
    session = requests.Session()
    
    # Make the HTTPS request with the specified timeout
    # The requests library automatically uses the system's CA bundle and performs 
    # certificate verification by default, which aligns with the SSL context policy
    response = session.get(
        endpoint_url,
        timeout=delay_limit,
        verify=True  # Explicitly ensure SSL verification is enabled
    )
    
    # Raise an exception for bad status codes
    response.raise_for_status()
    
    # Return the response content as a string
    return response.text

# Unittests
