import datetime
from typing import int

def remove_expired_sessions(expiration_duration: int) -> int:
    """
    Removes expired user sessions from the database that have surpassed the given expiration threshold.

    Args:
        expiration_duration: int, representing the duration in minutes beyond which a session is deemed expired.

    Returns:
        int: The total number of expired sessions that were successfully deleted.

    Security Consideration:
        This function uses a transaction with appropriate isolation level to ensure atomicity,
        preventing race conditions during high-traffic scenarios. The check and delete operations
        are performed within a single atomic block.
    """
    deleted_count = 0
    # Assuming a database connection is available via a context manager or global connection pool
    # This example uses a generic database interface (e.g., psycopg2, sqlite3, etc.)
    with get_database_connection() as conn:  # Replace with actual connection method
        with conn:  # This ensures transaction is used (context manager for transaction)
            cursor = conn.cursor()
            
            # Calculate the cutoff timestamp
            cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=expiration_duration)
            
            # Use a DELETE with WHERE condition in a single atomic statement to avoid race conditions
            # This is the safest approach: perform deletion based on timestamp directly
            delete_query = """
                DELETE FROM user_sessions 
                WHERE last_accessed < %s OR created_at < %s
            """
            # Use parameterized query to prevent SQL injection
            cursor.execute(delete_query, (cutoff_time, cutoff_time))
            
            deleted_count = cursor.rowcount
    
    return deleted_count


# Note: Replace `get_database_connection()` with your actual database connection function.
# Example for SQLite:
# def get_database_connection():
#     return sqlite3.connect('app.db')
#
# For PostgreSQL, you might use psycopg2.pool or similar.