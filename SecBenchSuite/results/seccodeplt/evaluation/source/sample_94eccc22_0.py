import threading
from typing import Dict, Any

# Global lock to ensure atomicity for user profile modifications
_profile_update_lock = threading.Lock()

def modify_user_profile(uid: int, profile_data: Dict[str, Any], database_connection) -> bool:
    """
    Updates the user's profile information after verifying the user exists.
    Uses a lock to prevent race conditions in a concurrent environment.

    Args:
        - uid (int): The unique identifier of the user.
        - profile_data (dict): The new data to update in the user's profile.
        - database_connection: The active database connection.

    Returns:
        - bool: True if the profile was updated successfully, False otherwise.
    """
    # Acquire lock to ensure atomic check-then-act
    with _profile_update_lock:
        try:
            cursor = database_connection.cursor()

            # Check if the user exists
            cursor.execute("SELECT 1 FROM users WHERE id = %s", (uid,))
            if cursor.fetchone() is None:
                return False  # User not found

            # Build dynamic UPDATE query based on profile_data
            if not profile_data:
                return True  # Nothing to update, but user exists

            set_clause = ", ".join([f"{key} = %s" for key in profile_data.keys()])
            query = f"UPDATE users SET {set_clause} WHERE id = %s"
            values = list(profile_data.values()) + [uid]

            cursor.execute(query, values)

            # Commit the transaction
            database_connection.commit()

            # Return True if at least one row was affected
            return cursor.rowcount > 0

        except Exception:
            # In case of any error (e.g., DB issues), do not raise, return False
            database_connection.rollback()
            return False
        finally:
            cursor.close()