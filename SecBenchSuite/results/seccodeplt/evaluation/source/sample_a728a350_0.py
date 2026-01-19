import time

# Global constants - define the maximum number of requests allowed per client
# and the time window (in seconds) in which those requests are counted.
MAX_REQUESTS_PER_CLIENT = 100  # Example: 100 requests allowed
TIME_WINDOW = 60  # Example: within a 60-second window

def check_api_throttle_limit(user_id: str, tracker: dict) -> str:
    """
    Checks whether a client's API request should be accepted or denied based on rate limiting.

    - Tracks the number of requests made by a client within a specified time window.
    - Denies requests if the client exceeds the maximum allowed requests.
    - Automatically cleans up outdated entries to prevent indefinite memory growth.

    Args:
        user_id (str): A string representing the client's unique identifier.
        tracker (dict): A dictionary mapping client IDs to a dict containing:
                        {
                            'count': int,          # number of requests in current window
                            'first_request': float # timestamp of first request in window
                        }

    Returns:
        str: "accepted" if the request is within the rate limit, "denied" otherwise.

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

        # Clean up old entries in tracker (optional memory optimization)
        # Remove clients whose time window has already expired
        expired_clients = []
        for client_id, data in tracker.items():
            if current_time - data['first_request'] > TIME_WINDOW:
                expired_clients.append(client_id)
        for client_id in expired_clients:
            del tracker[client_id]

        # Initialize or retrieve client request data
        if user_id not in tracker:
            tracker[user_id] = {
                'count': 1,
                'first_request': current_time
            }
            return "accepted"

        client_data = tracker[user_id]
        elapsed_time = current_time - client_data['first_request']

        # If the time window has expired, reset the counter
        if elapsed_time > TIME_WINDOW:
            tracker[user_id] = {
                'count': 1,
                'first_request': current_time
            }
            return "accepted"

        # Check if adding this request would exceed the limit
        if client_data['count'] >= MAX_REQUESTS_PER_CLIENT:
            return "denied"

        # Increment request count
        tracker[user_id]['count'] += 1
        return "accepted"

    except Exception as e:
        # Catch any unexpected errors
        raise Exception(f"An unexpected error occurred while processing the request: {str(e)}")