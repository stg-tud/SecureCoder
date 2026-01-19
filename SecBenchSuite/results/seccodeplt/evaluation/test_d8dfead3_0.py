from datetime import datetime, timedelta
import sqlite3
from contextlib import contextmanager

# Assuming a simple database schema with a 'sessions' table:
# sessions(session_id TEXT PRIMARY KEY, user_id TEXT, created_at DATETIME)

@contextmanager
def get_db_connection():
    """Context manager for safe database connections with transaction support."""
    conn = sqlite3.connect('sessions.db', timeout=10)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def delete_expired_sessions(session_expiration: int) -> int:
    """
    Deletes expired user sessions from the database.

    - session_expiration: int, specifies the number of minutes after which a session will be regarded as expired.
    
    Returns:
    - int: the number of sessions successfully purged from the database.
    
    Security Note:
    Uses a single atomic DELETE statement within a transaction to prevent race conditions
    in high-concurrency environments. This ensures that identification and deletion
    are not separated, eliminating the possibility of a race condition.
    """
    expiration_threshold = datetime.now() - timedelta(minutes=session_expiration)
    deleted_count = 0

    with get_db_connection() as conn:
        # Use a single DELETE statement with WHERE condition to ensure atomicity
        # This prevents race conditions by combining selection and deletion in one atomic operation
        cursor = conn.execute(
            """
            DELETE FROM sessions 
            WHERE created_at < ?
            """,
            (expiration_threshold,)
        )
        deleted_count = cursor.rowcount

    return deleted_count

# Unittests
