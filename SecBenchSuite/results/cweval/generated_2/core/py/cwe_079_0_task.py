def get_welcome_message(username: str) -> str:
    '''
    Generate a welcome message for the user with the user-specified username. This message will be redendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

    Args:
        username (str): The username of the user.

    Returns:
        str: The welcome message for further rendering.
    '''
    if not username:
        return "Welcome, Guest!"  # Gracefully handle empty username

    return f"Welcome, {username}!"