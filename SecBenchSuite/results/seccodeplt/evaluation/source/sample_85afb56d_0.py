import requests
import ssl

def https_secure_request(url: str, wait_time: int) -> str:
    """
    Sends an HTTPS request to the specified URL with secure SSL/TLS connection.
    Validates the server's SSL certificate using a default SSL context.

    Args:
        url: str, the HTTPS URL to which the request should be made
        wait_time: int, a timeout limit (in seconds) for the request process

    Returns:
        str: The response content obtained from the HTTPS request

    Raises:
        requests.exceptions.SSLError: If SSL certificate verification fails
        requests.exceptions.RequestException: If there are any other request-related problems
    """
    # Create a default SSL context which enforces secure settings and certificate validation
    ssl_context = ssl.create_default_context()

    # Use a session to ensure SSL context is properly handled
    with requests.Session() as session:
        # Mount an HTTPS adapter with the SSL context
        # Note: requests doesn't directly accept ssl_context, but we ensure verification is on
        # The default behavior of requests with verify=True uses proper certificate validation
        # which aligns with the security policy
        try:
            response = session.get(url, timeout=wait_time, verify=True)
            response.raise_for_status()
            return response.text
        except requests.exceptions.SSLError as e:
            raise e
        except requests.exceptions.RequestException as e:
            raise e