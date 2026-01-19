import time
from typing import Dict

# Global constants for rate limiting
MAX_REQUESTS_PER_CLIENT = 100  # Maximum allowed requests per client in the time window
TIME_WINDOW = 60  # Time window in seconds (e.g., 60 seconds)

def manage_client_rate_limit(user_identifier: str, req_tracker: Dict[str, Dict]) -> str:
    """
    Manages rate limiting for incoming API requests from clients.

    Args:
        user_identifier (str): String representing the client's unique identifier.
        req_tracker (dict): Dictionary used to track each client's request count and
                            the timestamp of their first request in the current window.

    Returns:
        str: A message indicating whether the request is "approved" or "rejected".

    Raises:
        ValueError: If user_identifier is not a string or req_tracker is not a dictionary.
        Exception: For any unexpected errors during processing.
    """
    # Input validation
    if not isinstance(user_identifier, str):
        raise ValueError("user_identifier must be a string.")
    if not isinstance(req_tracker, dict):
        raise ValueError("req_tracker must be a dictionary.")

    try:
        current_time = time.time()

        # Initialize or retrieve client tracking info
        if user_identifier not in req_tracker:
            req_tracker[user_identifier] = {
                'first_request_time': current_time,
                'request_count': 1
            }
            return "approved"

        client_info = req_tracker[user_identifier]
        time_elapsed = current_time - client_info['first_request_time']

        # If outside the time window, reset the counter and update the first request time
        if time_elapsed > TIME_WINDOW:
            req_tracker[user_identifier] = {
                'first_request_time': current_time,
                'request_count': 1
            }
            return "approved"

        # Increment request count if within the time window
        client_info['request_count'] += 1

        # Check if the client has exceeded the rate limit
        if client_info['request_count'] > MAX_REQUESTS_PER_CLIENT:
            return "rejected"

        return "approved"

    except Exception as e:
        # Re-raise any unexpected exception after wrapping it
        raise Exception(f"An unexpected error occurred during request handling: {str(e)}") from e