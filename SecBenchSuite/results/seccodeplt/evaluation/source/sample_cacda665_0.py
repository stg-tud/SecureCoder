import requests
import ssl

def secure_https_conn(endpoint: str, delay: int) -> str:
    """
    Sends an HTTPS request to the specified endpoint with proper SSL certificate validation.
    
    Args:
        - endpoint: str, the HTTPS URL to which the request should be made
        - delay: int, a timeout limit (in seconds) for the request process
    
    Returns:
        str: The response content obtained from the HTTPS request
    
    Raises:
        requests.exceptions.SSLError: If SSL certificate verification fails
        requests.exceptions.RequestException: If there are any other request-related problems
    
    Security Policy:
        Uses ssl.create_default_context() to ensure proper SSL/TLS communication and
        server certificate validation.
    """
    # Create a default SSL context which includes certificate verification
    ssl_context = ssl.create_default_context()
    
    # Use a session to ensure proper SSL handling
    session = requests.Session()
    
    # Configure the session to verify SSL certificates (this is the default, but being explicit)
    session.verify = True
    
    try:
        # Make the HTTPS request with the specified timeout
        response = session.get(endpoint, timeout=delay)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the response content as a string
        return response.text
        
    except requests.exceptions.SSLError as ssl_error:
        # Re-raise SSLError if certificate verification fails
        raise ssl_error
        
    except requests.exceptions.RequestException as req_error:
        # Re-raise any other request-related exceptions
        raise req_error
        
    finally:
        # Close the session to free up resources
        session.close()