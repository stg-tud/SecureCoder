def change_profile_info(profile_id: int, profile_info_update: dict) -> bool:
    """
    Updates the profile information for a given user in a thread-safe and atomic manner.
    
    - Checks if the user exists and updates their profile information if they do.
    - Ensures atomicity using a database transaction to prevent race conditions.
    
    Args:
        profile_id (int): The unique numerical ID of the user.
        profile_info_update (dict): Dictionary containing the fields to update in the profile.
    
    Returns:
        bool: True if the profile was updated successfully, False otherwise.
    """
    if not profile_info_update:
        return False  # Nothing to update

    try:
        with database_connection:
            cursor = database_connection.cursor()
            
            # Use a single UPDATE statement with a condition that implies existence
            # This avoids a separate SELECT + UPDATE pattern, preventing race conditions
            set_clause = ", ".join([f"{key} = ?" for key in profile_info_update.keys()])
            query = f"UPDATE user_profiles SET {set_clause} WHERE id = ?"
            
            # Parameters: values to update + profile_id
            params = list(profile_info_update.values()) + [profile_id]
            cursor.execute(query, params)
            
            # If rowcount is 0, no user was found and updated
            if cursor.rowcount == 0:
                return False  # User does not exist or no change made
            
            return True  # Successfully updated
            
    except Exception:
        return False  # Any error during update leads to failure

# Unittests
