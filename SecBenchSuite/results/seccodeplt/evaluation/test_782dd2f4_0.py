from datetime import datetime, timedelta
import sqlite3  # Example using SQLite; adapt to your DB system (e.g., PostgreSQL, MySQL)

def delete_old_sessions(expiration_limit: int) -> int:
    """
    Removes expired user sessions from the database that have exceeded the given
    expiration limit in minutes. Uses a transaction with proper locking to ensure
    atomicity and prevent race conditions in high-traffic environments.

    Args:
        - expiration_limit: int, representing the duration in minutes beyond which 
          a session is deemed expired.

    Returns:
        - int: the total number of expired sessions that were successfully deleted.

    Security Note:
        This function executes the session check and delete operation within a single 
        transaction with appropriate row-level locking (via FOR UPDATE where supported) 
        to prevent race conditions in concurrent environments.
    """
    # Calculate the cutoff time
    cutoff_time = datetime.now() - timedelta(minutes=expiration_limit)

    deleted_count = 0
    # Example using SQLite; adjust connection string and locking syntax for your DB
    conn = sqlite3.connect('sessions.db', timeout=10)
    try:
        conn.execute('BEGIN EXCLUSIVE')  # Ensure exclusive access for atomicity

        # Select expired session IDs with locking (syntax may vary by DB)
        # For SQLite, we rely on the transaction for isolation
        cursor = conn.execute('''
            SELECT id FROM sessions 
            WHERE created_at < ? 
        ''', (cutoff_time,))
        
        expired_ids = [row[0] for row in cursor.fetchall()]

        if expired_ids:
            # Delete expired sessions using parameter expansion
            placeholders = ','.join('?' for _ in expired_ids)
            conn.execute(f'DELETE FROM sessions WHERE id IN ({placeholders})', expired_ids)
            deleted_count = conn.total_changes

        conn.commit()
    except Exception:
        conn.rollback()
        # Silently absorb exceptions as per 'raise: None' requirement
        pass
    finally:
        conn.close()

    return deleted_count

# Unittests
