from datetime import datetime, timedelta
import sqlite3

def remove_old_sessions(time_limit: int) -> int:
    """
    Removes expired user sessions from the database based on the given time limit.

    Parameters:
        time_limit (int): The session expiration time in minutes.

    Returns:
        int: The count of successfully deleted expired sessions.

    Security Note:
        This function uses an atomic DELETE operation with a WHERE clause to prevent race conditions
        in high-concurrency environments. The operation is performed in a single transaction to ensure
        consistency and avoid non-atomic check-then-delete patterns.
    """
    # Calculate the cutoff timestamp for expired sessions
    cutoff_time = datetime.now() - timedelta(minutes=time_limit)
    
    deleted_count = 0
    
    # Use atomic transaction to avoid race conditions
    conn = sqlite3.connect('app_database.db')
    try:
        cursor = conn.cursor()
        
        # Atomic delete: remove sessions where last_activity is older than cutoff_time
        cursor.execute("""
            DELETE FROM user_sessions 
            WHERE last_activity < ?
        """, (cutoff_time,))
        
        deleted_count = cursor.rowcount
        conn.commit()
    except Exception:
        # In case of any error, rollback to ensure consistency
        conn.rollback()
    finally:
        conn.close()
    
    return deleted_count