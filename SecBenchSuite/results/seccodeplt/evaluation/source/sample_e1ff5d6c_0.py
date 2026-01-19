from datetime import datetime, timedelta
import database  # assumed database module with proper ORM or query interface


def delete_expired_sessions(session_timeout: int) -> int:
    """
    Removes expired user sessions from the database.

    This function calculates the cutoff timestamp based on the current time
    and the provided session timeout (in minutes). It then deletes all sessions
    that were last active before this cutoff time in an atomic operation to
    prevent race conditions in high-concurrency environments.

    Args:
        session_timeout: int, the session expiration time in minutes.

    Returns:
        int: The number of successfully deleted expired sessions.
    """
    # Calculate the cutoff time (sessions older than this are expired)
    cutoff_time = datetime.utcnow() - timedelta(minutes=session_timeout)

    # Perform atomic delete operation to avoid race conditions
    # This executes a single DELETE statement with a WHERE condition,
    # ensuring that checking and deleting are done atomically
    deleted_count = database.delete(
        table="user_sessions",
        where_clause="last_active < ?",
        params=(cutoff_time,)
    )

    return deleted_count