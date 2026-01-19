import datetime
from typing import int

def purge_expired_sessions(expire_duration: int) -> int:
    """
    Removes expired user sessions from the database.

    This function identifies all sessions where the last activity timestamp
    is older than the specified expire_duration (in minutes) and deletes them
    in an atomic transaction to prevent race conditions in high-concurrency environments.

    Args:
        expire_duration: int, specifies the number of minutes after which a session 
                         will be regarded as expired.

    Returns:
        int: The number of sessions successfully purged from the database.

    Security Note:
        The operation is performed within a database transaction to ensure atomicity.
        This prevents race conditions where a session might be re-activated between
        the check and delete phases in high-concurrency scenarios.
    """
    # Calculate the cutoff timestamp
    cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=expire_duration)
    
    # Use a transaction to ensure atomicity of select and delete operations
    # Example using a hypothetical database connection (e.g., SQLite, PostgreSQL)
    conn = get_database_connection()  # Assume this returns a valid DB connection
    try:
        with conn:
            cursor = conn.cursor()
            # Atomic delete of expired sessions
            cursor.execute("""
                DELETE FROM user_sessions 
                WHERE last_activity < ?
            """, (cutoff_time,))
            
            # Return the number of deleted rows
            return cursor.rowcount
    finally:
        conn.close()