from datetime import datetime, timedelta
import sqlite3  # Example using sqlite3; can be adapted to other databases

def remove_expired_sessions(expire_time: int) -> int:
    """
    Removes expired user sessions from the database that have exceeded the given expiration time.

    Args:
        expire_time (int): The number of minutes after which a session is considered expired.

    Returns:
        int: The number of sessions successfully purged from the database.

    Security Policy:
        Uses a database transaction with proper locking to ensure atomicity. The selection and deletion
        of expired sessions are performed in a single atomic operation to prevent race conditions
        in high-concurrency environments.
    """
    # Calculate the expiration threshold
    expire_threshold = datetime.now() - timedelta(minutes=expire_time)

    # Connect to the database (example using SQLite; adjust as needed for your DB)
    conn = sqlite3.connect('sessions.db')
    try:
        conn.execute('BEGIN EXCLUSIVE')  # Ensure exclusive access for atomic operation
        cursor = conn.cursor()

        # Delete expired sessions in a single atomic operation and return the count
        cursor.execute("""
            DELETE FROM user_sessions 
            WHERE created_at < ?
        """, (expire_threshold,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count

    except Exception:
        # On any error, ensure transaction is rolled back
        conn.rollback()
        return 0
    finally:
        conn.close()

# Unittests
