import threading

# Lock to ensure atomicity between existence check and update in a multi-threaded environment
_profile_update_lock = threading.Lock()

def edit_user_profile(user_identifier: int, profile_information: dict) -> bool:
    """
    Updates the profile of a user given their identifier and new profile information.
    
    Ensures atomicity using a lock to prevent race conditions in a concurrent environment.
    
    Args:
        user_identifier (int): Unique identifier of the user whose profile needs updating.
        profile_information (dict): Contains the new data for the user's profile.
    
    Returns:
        bool: True if the profile is updated successfully, False if the user is not found
              or the update fails.
    
    Note:
        This function does not raise exceptions. It returns False on any failure.
    """
    # Acquire lock to prevent race condition between existence check and update
    with _profile_update_lock:
        try:
            # Verify if the user exists
            query_check = "SELECT 1 FROM users WHERE id = %s"
            with database_connection.cursor() as cursor:
                cursor.execute(query_check, (user_identifier,))
                if cursor.fetchone() is None:
                    return False  # User not found
            
            # Perform the profile update
            # Dynamically build the SET clause from profile_information
            set_clause = ", ".join([f"{key} = %s" for key in profile_information.keys()])
            query_update = f"UPDATE users SET {set_clause} WHERE id = %s"
            
            # Execute update with the new profile data
            with database_connection.cursor() as cursor:
                cursor.execute(query_update, (*profile_information.values(), user_identifier))
                database_connection.commit()
            
            # Confirm that at least one row was updated
            return cursor.rowcount > 0
        
        except Exception:
            # In case of any error (DB issues, connection problems, etc.), return False
            try:
                database_connection.rollback()
            except:
                pass  # Ignore rollback errors
            return False

# Unittests
