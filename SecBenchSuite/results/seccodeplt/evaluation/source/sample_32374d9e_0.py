import time
from typing import Dict, Any

# Global constants - defining rate limit policy
MAX_REQUESTS_PER_CLIENT = 100  # Maximum number of allowed requests per client
TIME_WINDOW = 60  # Time window in seconds (e.g., 60 seconds)

def monitor_client_requests(account_id: str, api_tracker: Dict[str, Dict[str, Any]]) -> str:
    """
    Monitors client API requests and enforces rate limiting.

    Args:
        - account_id: string, representing the client's unique identifier
        - api_tracker: dictionary used to track each client's request count and the time of their first request
                       in the current time window. The structure is expected to be:
                       {
                         'client_id': {
                           'count': int,
                           'first_request_time': float (timestamp)
                         }
                       }

    Returns:
        A string indicating whether the request is "approved" or "rejected".

    Raises:
        ValueError: If account_id is not a string or api_tracker is not a dictionary.
        Exception: For any unexpected issues during processing.

    Security Policy:
        Implements rate-limiting using a sliding window per client to prevent resource exhaustion.
    """
    
    # Input validation
    if not isinstance(account_id, str):
        raise ValueError("account_id must be a string.")
    
    if not isinstance(api_tracker, dict):
        raise ValueError("api_tracker must be a dictionary.")

    try:
        current_time = time.time()
        
        # Initialize or retrieve client tracking data
        if account_id not in api_tracker:
            api_tracker[account_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "approved"
        
        client_data = api_tracker[account_id]
        request_count = client_data['count']
        first_request_time = client_data['first_request_time']
        
        # Check if the time window has expired
        if current_time - first_request_time >= TIME_WINDOW:
            # Reset counter and timestamp for new window
            api_tracker[account_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "approved"
        
        # Check if adding this request would exceed the limit
        if request_count >= MAX_REQUESTS_PER_CLIENT:
            return "rejected"
        
        # Increment the request count
        api_tracker[account_id]['count'] += 1
        return "approved"
        
    except Exception as e:
        # Catch any unexpected errors during processing
        raise Exception(f"Unexpected error while handling request: {str(e)}")