from datetime import datetime, timedelta
import sqlite3
from typing import Optional

def purge_stale_sessions(expiry_time: int) -> int:
    """
    Removes expired user sessions from the database that have surpassed the given expiration threshold.
    
    Parameters:
        expiry_time (int): Duration in minutes beyond which a session is deemed expired.
    
    Returns:
        int: The total number of expired sessions that were successfully deleted.
    
    Security Note:
        This function uses a database transaction to ensure atomicity. The SELECT and DELETE operations
        are encapsulated within a single transaction to prevent race conditions in high-traffic environments.
        Proper row-level or table locking is relied upon via the database's isolation mechanisms.
    """
    # Assuming a SQLite database; adjust connection as needed for your environment
    conn: Optional[sqlite3.Connection] = None
    deleted_count = 0

    try:
        conn = sqlite3.connect('app_database.db')  # Replace with your DB path or connection method
        conn.isolation_level = 'DEFERRED'  # Ensures transaction-level consistency

        cursor = conn.cursor()

        # Calculate the cutoff timestamp
        cutoff_time = datetime.now() - timedelta(minutes=expiry_time)

        # Use a transaction to maintain atomicity of check-and-delete
        cursor.execute('BEGIN IMMEDIATE;')

        # Delete expired sessions in a single atomic operation
        # Assume table name is 'user_sessions' with a 'created_at' or 'last_active' timestamp field
        cursor.execute('''
            DELETE FROM user_sessions 
            WHERE last_active < ?
        ''', (cutoff_time,))

        deleted_count = cursor.rowcount

        # Commit the transaction
        conn.commit()

    except Exception:
        # On error, rollback to maintain consistency (even though function shouldn't raise)
        if conn:
            try:
                conn.rollback()
            except:
                pass
        # Silently handle exceptions per requirement: do not raise
        deleted_count = 0

    finally:
        if conn:
            conn.close()

    return deleted_count