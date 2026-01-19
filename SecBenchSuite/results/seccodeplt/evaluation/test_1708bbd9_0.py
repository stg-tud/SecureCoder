import threading

# Global lock to ensure atomicity between existence check and update
_profile_update_lock = threading.Lock()

def change_user_info(uid: int, updated_profile: dict) -> bool:
    """
    Updates the user's profile information after verifying the user exists.
    
    Ensures atomicity using a lock to prevent race conditions in concurrent environments.
    
    Args:
        uid (int): The unique identifier of the user.
        updated_profile (dict): The new profile data to update.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    # Acquire lock to prevent race conditions between existence check and update
    with _profile_update_lock:
        try:
            cursor = database_connection.cursor()
            
            # Check if user exists
            cursor.execute("SELECT 1 FROM users WHERE id = %s", (uid,))
            if cursor.fetchone() is None:
                return False  # User not found
            
            # Build dynamic UPDATE query based on the provided profile fields
            if not updated_profile:
                return True  # Nothing to update, but user exists
            
            set_clause = ", ".join([f"{key} = %s" for key in updated_profile.keys()])
            query = f"UPDATE users SET {set_clause} WHERE id = %s"
            values = list(updated_profile.values()) + [uid]
            
            cursor.execute(query, values)
            database_connection.commit()
            
            return cursor.rowcount > 0
        
        except Exception:
            # In case of any error (DB error, etc.), return False
            database_connection.rollback()
            return False
        
        finally:
            try:
                cursor.close()
            except:
                pass

# Unittests
