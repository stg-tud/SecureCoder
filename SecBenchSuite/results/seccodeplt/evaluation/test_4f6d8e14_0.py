def change_user_profile(user_identifier: int, fresh_profile_data: dict, database_connection) -> bool:
    """
    Updates a user's profile in a thread-safe and atomic manner.

    - Checks if the user exists and updates their profile in a single atomic operation.
    - Uses a database transaction to ensure atomicity and prevent race conditions.
    - Returns True on success, False otherwise.

    Args:
        user_identifier: int, the user identifier whose profile must be updated.
        fresh_profile_data: dict, the new information to be used for updating the user's profile.
        database_connection: Active database connection with transaction support.

    Returns:
        bool: True if the profile update was successful, False otherwise.
    """
    if not fresh_profile_data:
        return False  # Nothing to update

    try:
        with database_connection:
            cursor = database_connection.cursor()
            
            # Use a single UPDATE statement with a WHERE clause that verifies user existence
            # This ensures atomicity: update only happens if user exists
            set_clause = ", ".join([f"{key} = ?" for key in fresh_profile_data.keys()])
            query = f"UPDATE users SET {set_clause} WHERE user_id = ?"
            
            # Parameters: fresh_profile_data values followed by user_identifier
            params = list(fresh_profile_data.values()) + [user_identifier]
            
            cursor.execute(query, params)
            
            # Check if any row was actually updated
            if cursor.rowcount == 0:
                return False  # User not found or no changes made
            
            return True
    except Exception:
        # Silently return False on any error (per requirement: does not raise exceptions)
        return False

# Unittests
