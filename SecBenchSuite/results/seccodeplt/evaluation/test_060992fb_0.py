import time

# Global constants (typically defined at module level)
MAX_REQUESTS_PER_CLIENT = 100  # Maximum number of requests allowed per client
TIME_WINDOW = 60  # Time window in seconds (e.g., 60 seconds)

def api_rate_control(cid: str, tracker: dict) -> str:
    """
    Controls API access based on rate limiting per client.

    Args:
        - cid: A string representing the unique identifier of each client.
        - tracker: A dictionary tracking the number of requests each client has made
                   and the timestamp of their earliest request within the current period.
                   Format: {client_id: {'count': int, 'first_request_time': float}}}

    Returns:
        A string indicating whether the client's request has been 'accepted' or 'denied'.

    Raises:
        ValueError: If input data is invalid.
        Exception: For unexpected errors during processing.
    """
    # Input validation
    if not isinstance(cid, str):
        raise ValueError("Client ID (cid) must be a string.")
    if not isinstance(tracker, dict):
        raise ValueError("Tracker must be a dictionary.")
    if cid == "":
        raise ValueError("Client ID (cid) cannot be an empty string.")

    current_time = time.time()

    try:
        # Initialize or retrieve client tracking data
        if cid not in tracker:
            tracker[cid] = {'count': 1, 'first_request_time': current_time}
            return "accepted"

        client_info = tracker[cid]
        request_count = client_info['count']
        first_request_time = client_info['first_request_time']

        # Check if the current time is still within the time window
        if current_time - first_request_time < TIME_WINDOW:
            # Within the time window
            if request_count >= MAX_REQUESTS_PER_CLIENT:
                return "denied"  # Rate limit exceeded
            else:
                # Increment the request count
                tracker[cid]['count'] += 1
                return "accepted"
        else:
            # Outside the time window – reset the counter
            tracker[cid] = {'count': 1, 'first_request_time': current_time}
            return "accepted"

    except Exception as e:
        # Catch any unexpected error during processing
        raise Exception(f"Error processing request for client {cid}: {str(e)}")

# Unittests
