import time
from typing import Dict

# Global constants for rate limiting
MAX_REQUESTS_PER_CLIENT = 100  # Maximum number of allowed requests per client within the time window
TIME_WINDOW = 60  # Time window in seconds (e.g., 60 seconds)

def enforce_api_rate_cap(customer_id: str, api_tracker: Dict[str, Dict]) -> str:
    """
    Enforces API rate limiting for a given client.

    Args:
        customer_id (str): A string representing each client's unique identifier.
        api_tracker (dict): A dictionary that maps client IDs to a dictionary containing:
                            - 'count': the number of requests made in the current time window
                            - 'first_request_time': the timestamp of the first request in the window

    Returns:
        str: "ACCEPTED" if the request is within the rate limit, "DENIED" otherwise.

    Raises:
        ValueError: If inputs are invalid (e.g., customer_id not a string, api_tracker not a dict).
        Exception: For any unexpected internal errors.
    """
    # Input validation
    if not isinstance(customer_id, str):
        raise ValueError("customer_id must be a string.")
    if not isinstance(api_tracker, dict):
        raise ValueError("api_tracker must be a dictionary.")
    if not isinstance(MAX_REQUESTS_PER_CLIENT, int) or MAX_REQUESTS_PER_CLIENT <= 0:
        raise ValueError("MAX_REQUESTS_PER_CLIENT must be a positive integer.")
    if not isinstance(TIME_WINDOW, int) or TIME_WINDOW <= 0:
        raise ValueError("TIME_WINDOW must be a positive integer.")

    current_time = time.time()

    try:
        # Initialize or retrieve client tracking data
        if customer_id not in api_tracker:
            api_tracker[customer_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "ACCEPTED"

        client_data = api_tracker[customer_id]
        request_count = client_data['count']
        first_request_time = client_data['first_request_time']

        # Check if the current request falls within the time window
        if current_time - first_request_time >= TIME_WINDOW:
            # Time window has expired; reset counter
            api_tracker[customer_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "ACCEPTED"
        else:
            # Still within the time window
            if request_count < MAX_REQUESTS_PER_CLIENT:
                # Increment the request count
                api_tracker[customer_id]['count'] += 1
                return "ACCEPTED"
            else:
                # Rate limit exceeded
                return "DENIED"

    except Exception as e:
        # Catch any unexpected errors during processing
        raise Exception(f"An unexpected error occurred while processing the request: {str(e)}")

# Unittests
