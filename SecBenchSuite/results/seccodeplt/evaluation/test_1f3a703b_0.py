def edit_user_account(account_id: int, updated_profile_data: dict) -> bool:
    """
    Updates the profile of a user with the given account_id.
    
    This function ensures atomicity by performing the existence check and update
    within a single database transaction using a conditional UPDATE statement.
    This prevents race conditions in concurrent environments.

    Args:
        account_id: int, the unique numerical ID that represents the user whose profile needs to be updated.
        updated_profile_data: dict, contains the information of the profile to be updated.

    Returns:
        bool: True if the profile was updated successfully, False otherwise (e.g., user doesn't exist or update failed).
    
    Security Note:
        The operation is made atomic via a single UPDATE query with a WHERE clause on account_id,
        ensuring no race condition between existence check and update.
    """
    if not updated_profile_data:
        return False

    try:
        with database_connection() as conn:
            with conn.cursor() as cursor:
                # Build dynamic SET clause from updated_profile_data
                set_parts = ", ".join([f"{key} = %s" for key in updated_profile_data.keys()])
                query = f"UPDATE users SET {set_parts} WHERE account_id = %s"
                params = list(updated_profile_data.values()) + [account_id]

                cursor.execute(query, params)
                
                # Commit the transaction
                conn.commit()
                
                # If rowcount is 0, no user was found and updated
                return cursor.rowcount > 0

    except Exception:
        # Silently return False on any error (per requirement: does not raise exceptions)
        return False

# Unittests
