import time

# Global constants - define the rate limiting policy
MAX_REQUESTS_PER_CLIENT = 100  # Maximum number of allowed requests per client within the time window
TIME_WINDOW = 60  # Time window in seconds (e.g., 60 seconds)

def limit_api_usage(account_id: str, usage_log: dict) -> str:
    """
    Limits API usage based on rate limiting rules.

    Args:
        account_id (str): A string representing each client's unique identifier.
        usage_log (dict): A dictionary that maps client IDs to a dictionary containing:
                          - 'count': the number of requests made by the client
                          - 'first_request_time': timestamp of the first request in the window

    Returns:
        str: "Accepted" if the request is within the rate limit, "Denied" otherwise.

    Raises:
        ValueError: If inputs are not valid.
        Exception: For any unexpected errors during processing.
    """
    # Input validation
    if not isinstance(account_id, str):
        raise ValueError("account_id must be a string.")
    if not isinstance(usage_log, dict):
        raise ValueError("usage_log must be a dictionary.")

    current_time = time.time()

    try:
        # Initialize or retrieve client's request record
        if account_id not in usage_log:
            usage_log[account_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "Accepted"

        client_data = usage_log[account_id]
        request_count = client_data['count']
        first_request_time = client_data['first_request_time']

        # Check if the time window has expired
        if current_time - first_request_time > TIME_WINDOW:
            # Reset the counter and update the first request time to current
            usage_log[account_id] = {
                'count': 1,
                'first_request_time': current_time
            }
            return "Accepted"

        # Check if client has exceeded the request limit
        if request_count >= MAX_REQUESTS_PER_CLIENT:
            return "Denied"

        # Increment the request count
        usage_log[account_id]['count'] += 1
        return "Accepted"

    except Exception as e:
        # Catch any unexpected errors
        raise Exception(f"An unexpected error occurred while processing the request: {str(e)}") from e