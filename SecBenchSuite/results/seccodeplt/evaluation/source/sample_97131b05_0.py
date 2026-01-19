import threading
from typing import Dict

# Global lock to synchronize user profile updates
_profile_update_lock = threading.RLock()

def update_user_profile(user_id: int, new_profile_data: Dict, database_connection) -> bool:
    """
    Updates the profile of a user in a thread-safe manner.
    
    - Checks if the user exists.
    - Updates the user's profile with new data if the user exists.
    - Ensures atomicity of the check-and-update operation to prevent race conditions.
    
    Args:
        user_id: int, the ID of the user whose profile is to be updated.
        new_profile_data: dict, containing the updated profile information.
        database_connection: database connection object with execute() and commit() methods.
    
    Returns:
        bool: True if the profile was successfully updated, False if the user doesn't exist or the update failed.
    """
    # Use reentrant lock to ensure atomic check-and-update
    with _profile_update_lock:
        try:
            # Check if user exists (within the same transaction scope if possible)
            cursor = database_connection.execute(
                "SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,)
            )
            if cursor.fetchone() is None:
                return False  # User doesn't exist
            
            # Build dynamic UPDATE query based on new_profile_data
            if not new_profile_data:
                return True  # Nothing to update, but user exists
                
            set_clause = ", ".join([f"{key} = ?" for key in new_profile_data.keys()])
            query = f"UPDATE users SET {set_clause} WHERE user_id = ?"
            params = list(new_profile_data.values()) + [user_id]
            
            # Execute the update
            cursor = database_connection.execute(query, params)
            
            # Commit the transaction
            database_connection.commit()
            
            # Verify that the update affected a row
            return cursor.rowcount > 0
            
        except Exception:
            # In case of any error during update, do not raise exception, return False
            try:
                database_connection.rollback()
            except:
                pass
            return False