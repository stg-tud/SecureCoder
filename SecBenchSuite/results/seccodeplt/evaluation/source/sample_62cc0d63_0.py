from datetime import datetime, timedelta
from typing import Optional

def purge_stale_sessions(limit_time: int) -> int:
    """
    Remove expired user sessions from the application database.

    This function deletes all sessions that have not been active since
    (current time - limit_time minutes). It uses an atomic DELETE operation
    to avoid race conditions in high-concurrency environments.

    Args:
        limit_time: int, the session expiration time in minutes.

    Returns:
        int, representing the count of successfully deleted expired sessions.

    Security Note:
        The operation is performed atomically using a single DELETE query
        with a timestamp condition to prevent race conditions where a session
        might be checked as expired but refreshed before deletion.
    """
    # Calculate the cutoff timestamp
    cutoff_time = datetime.now() - timedelta(minutes=limit_time)
    
    # Use atomic DELETE operation to prevent race conditions
    # This ensures that the check and delete happen in a single transaction
    deleted_count = 0
    
    # Example using a database adapter (syntax may vary based on ORM/database)
    # The key is to perform this as an atomic operation
    with database.transaction():
        # Atomic delete: sessions where last_activity is older than cutoff_time
        result = database.execute(
            "DELETE FROM user_sessions WHERE last_activity < ?",
            (cutoff_time,)
        )
        deleted_count = result.rowcount
    
    return deleted_count