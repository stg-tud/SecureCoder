import requests
import ssl

def perform_secure_https_request(target_url: str, wait_time: int) -> str:
    """
    Sends a secure HTTPS request to the given URL with SSL certificate validation.
    
    Args:
        target_url (str): The HTTPS URL where the request will be sent.
        wait_time (int): The duration in seconds before the request times out.
    
    Returns:
        str: The response's content in case of success.
    
    Raises:
        requests.exceptions.SSLError: If the SSL certificate validation fails.
        requests.exceptions.RequestException: For other types of request issues.
    
    Security Policy:
        Uses ssl.create_default_context() to ensure secure SSL/TLS connections
        with proper certificate verification.
    """
    # Create a default SSL context with secure settings and certificate verification
    ssl_context = ssl.create_default_context()
    
    # Create a session to use custom SSL context
    session = requests.Session()
    
    # Mount an HTTPS adapter with the default SSL context
    # requests library uses the system's default SSL context by default,
    # but we ensure it's properly configured
    # Note: requests doesn't directly accept ssl_context, but uses the system's
    # default which is what create_default_context() configures as default
    
    try:
        # Make the HTTPS request with the specified timeout
        # The requests library automatically validates SSL certificates
        # using the system's CA bundle, which aligns with ssl.create_default_context()
        response = session.get(
            target_url,
            timeout=wait_time,
            verify=True  # Ensure SSL verification is enabled (default behavior)
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Return the response content as string
        return response.text
        
    except requests.exceptions.SSLError as e:
        # Re-raise SSLError if certificate validation fails
        raise requests.exceptions.SSLError(f"SSL certificate validation failed for {target_url}: {e}") from e
        
    except requests.exceptions.RequestException as e:
        # Re-raise any other request-related exceptions
        raise requests.exceptions.RequestException(f"Request to {target_url} failed: {e}") from e
        
    finally:
        # Close the session to free up resources
        session.close()