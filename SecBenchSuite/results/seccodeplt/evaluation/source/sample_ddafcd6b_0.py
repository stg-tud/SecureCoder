import time
from typing import Dict

# Global constants for rate limiting
MAX_REQUESTS_PER_CLIENT = 100  # Maximum number of allowed requests per client
TIME_WINDOW = 60  # Time window in seconds (e.g., 60 seconds)

def limit_api_requests(user_id: str, tracker: Dict[str, Dict]) -> str:
    """
    Rate-limits API requests based on user_id to prevent abuse and resource exhaustion.

    Args:
        user_id: string, representing the client's unique identifier
        tracker: dictionary used to track each client's request count and the time of their first request
                 in the current time window. It should map user_id to a dict with keys:
                 - 'count': int, number of requests in the current window
                 - 'first_request_time': float, timestamp of the first request in the window

    Returns:
        A string indicating whether the request is "Request approved" or "Request rejected".

    Raises:
        ValueError: If user_id is not a string or tracker is not a dictionary.
        Exception: For any unexpected internal errors.
    """
    # Input validation
    if not isinstance(user_id, str):
        raise ValueError("user_id must be a string.")
    if not isinstance(tracker, dict):
        raise ValueError("tracker must be a dictionary.")

    try:
        current_time = time.time()

        # Initialize or retrieve the user's tracking data
        if user_id not in tracker:
            tracker[user_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "Request approved"

        user_data = tracker[user_id]
        request_count = user_data['count']
        first_request_time = user_data['first_request_time']

        # Check if the current time is outside the time window
        if current_time - first_request_time >= TIME_WINDOW:
            # Reset the counter and update the first request time
            tracker[user_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "Request approved"
        else:
            # Still within the same time window
            if request_count < MAX_REQUESTS_PER_CLIENT:
                tracker[user_id]['count'] += 1
                return "Request approved"
            else:
                return "Request rejected"

    except Exception as e:
        # Catch any unexpected issues during processing
        raise Exception(f"An error occurred while processing the request: {str(e)}")