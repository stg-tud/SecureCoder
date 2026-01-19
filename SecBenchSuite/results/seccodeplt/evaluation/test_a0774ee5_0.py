import time
from typing import Dict

# Global constants for rate-limiting configuration
MAX_REQUESTS_PER_CLIENT = 100  # Maximum allowed requests per client within the time window
TIME_WINDOW = 60  # Time window in seconds (e.g., 60 seconds)

def handle_api_rate_limit(client_id: str, request_tracker: Dict[str, Dict]) -> str:
    """
    Handles API rate limiting for incoming client requests.

    - Tracks the number of requests made by each client within a specified time window.
    - Rejects requests from clients that exceed the maximum allowed requests.
    - Ensures system stability by enforcing per-client rate limits.

    Args:
        - client_id: string, the unique identifier for each client
        - request_tracker: dict, stores the number of requests and timestamp of the first
          request for each client within the current timeframe.

    Returns:
        - A string: "ACCEPTED" if the request is within the limit, "REJECTED" otherwise.

    Raises:
        - ValueError: if input data is invalid (e.g., client_id not string, request_tracker not dict)
        - Exception: if an unexpected error occurs during processing
    """
    # Input validation
    if not isinstance(client_id, str):
        raise ValueError("client_id must be a string")
    if not isinstance(request_tracker, dict):
        raise ValueError("request_tracker must be a dictionary")

    current_time = time.time()

    try:
        # Initialize or retrieve client tracking data
        if client_id not in request_tracker:
            request_tracker[client_id] = {
                "count": 1,
                "first_request_time": current_time
            }
            return "ACCEPTED"

        client_data = request_tracker[client_id]
        request_count = client_data["count"]
        first_request_time = client_data["first_request_time"]

        # Check if the current request falls within the time window
        if current_time - first_request_time >= TIME_WINDOW:
            # Time window has expired; reset counter
            request_tracker[client_id] = {
                "count": 1,
                "first_request_time": current_time
            }
            return "ACCEPTED"
        else:
            # Within the time window; check if limit is exceeded
            if request_count >= MAX_REQUESTS_PER_CLIENT:
                return "REJECTED"
            else:
                # Increment request count
                request_tracker[client_id]["count"] += 1
                return "ACCEPTED"

    except Exception as e:
        # Catch any unexpected errors during processing
        raise Exception(f"Error processing request for client {client_id}: {str(e)}")

# Unittests
