import time
from typing import Dict, Any

# Global constants for rate-limiting behavior
MAX_REQUESTS_PER_CLIENT = 100  # Maximum allowed requests per client within the time window
TIME_WINDOW = 60  # Time window in seconds

def client_request_manager(client_identifier: str, request_data: Dict[str, Any]) -> str:
    """
    Manages API requests made by different clients, enforcing rate limits based on MAX_REQUESTS_PER_CLIENT
    and TIME_WINDOW. Prevents clients from exceeding the allowed number of requests in the given time period.

    Args:
        - client_identifier: A string representing the unique identifier of each client
        - request_data: A dictionary tracking:
            - 'count': the number of requests the client has made in the current period
            - 'first_request_timestamp': the timestamp of the earliest request in the current period

    Returns:
        A string indicating whether the client's request has been accepted or denied.

    Raises:
        ValueError: If input data is invalid (e.g., missing fields, incorrect types).
        Exception: For any other errors during processing.
    """
    
    # Input validation
    if not isinstance(client_identifier, str):
        raise ValueError("client_identifier must be a string.")
    
    if not isinstance(request_data, dict):
        raise ValueError("request_data must be a dictionary.")
    
    if 'count' not in request_data or 'first_request_timestamp' not in request_data:
        raise ValueError("request_data must contain 'count' and 'first_request_timestamp' keys.")
    
    try:
        request_count = request_data['count']
        first_timestamp = request_data['first_request_timestamp']
        
        if not isinstance(request_count, int) or request_count < 0:
            raise ValueError("'count' in request_data must be a non-negative integer.")
        
        if not isinstance(first_timestamp, (int, float)):
            raise ValueError("'first_request_timestamp' must be a numeric value (timestamp).")
        
        current_time = time.time()
        
        # Check if the time window has expired
        if current_time - first_timestamp > TIME_WINDOW:
            # Time window expired; reset count (new period)
            return "Request accepted (new time window)."
        
        # Check if client has exceeded the maximum allowed requests
        if request_count >= MAX_REQUESTS_PER_CLIENT:
            return "Request denied. Rate limit exceeded."
        
        # Accept the request
        return "Request accepted."

    except ValueError:
        # Re-raise ValueErrors from validation
        raise
    except Exception as e:
        # Catch any other unforeseen processing errors
        raise Exception(f"Error processing request for client {client_identifier}: {str(e)}")

# Unittests
