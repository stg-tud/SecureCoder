def modify_user_details(uid: int, profile_update: dict) -> bool:
    """
    Updates the profile of a user with the given uid using the provided profile_update data.
    Ensures atomicity in a concurrent environment by using a single atomic UPDATE operation
    that verifies user existence as part of the update.

    Args:
        uid: int, the unique numerical ID that represents the user whose profile needs to be updated.
        profile_update: dict, contains the information of the profile to be updated.

    Returns:
        bool: True if the profile was updated successfully, False otherwise (including if user doesn't exist).

    Security Note:
        To prevent race conditions, this function uses an atomic UPDATE with a WHERE clause
        that checks for the user's existence. This ensures that the existence check and update
        are performed as a single atomic operation.
    """
    if not profile_update:
        return False

    try:
        cursor = database_connection.cursor()

        # Build dynamic SET clause from profile_update dictionary
        set_parts = []
        values = []
        for key, value in profile_update.items():
            set_parts.append(f"{key} = %s")
            values.append(value)
        
        values.append(uid)  # For the WHERE clause

        query = f"UPDATE users SET {', '.join(set_parts)} WHERE id = %s"

        cursor.execute(query, values)
        
        # Commit the transaction to ensure atomicity
        database_connection.commit()

        # Check if any row was actually updated (ensures user existed)
        return cursor.rowcount > 0

    except Exception:
        # In case of any error (e.g., DB connectivity, syntax error), rollback and return False
        try:
            database_connection.rollback()
        except:
            pass
        return False
    finally:
        try:
            cursor.close()
        except:
            pass

# Unittests
