import datetime
from typing import int

def clean_expired_sessions(expiration_time: int) -> int:
    """
    Cleans up expired user sessions from the database.
    
    Uses a database transaction to ensure atomicity of the check-and-remove operation,
    preventing race conditions in high-traffic environments.
    
    Args:
        expiration_time: int, the number of minutes after which a session is considered expired.
        
    Returns:
        int: the number of expired sessions that were successfully removed.
    """
    # Calculate the cutoff timestamp for expired sessions
    cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=expiration_time)
    
    # Use a transaction to ensure atomicity of the check-and-delete operation
    # This prevents race conditions where sessions might be accessed between check and delete
    try:
        # Begin transaction (syntax may vary based on the database library used)
        # Example using a generic database connection:
        with database.transaction():
            # Select and delete expired sessions in a single atomic operation
            # This approach minimizes the window for race conditions
            result = database.execute(
                "DELETE FROM sessions WHERE created_at < ?",
                (cutoff_time,)
            )
            
            # Return the number of deleted rows
            return result.rowcount
            
    except Exception:
        # If using a context that automatically handles rollback on exception,
        # the transaction will be safely rolled back
        # We don't raise exceptions as specified in the requirements
        return 0

# Unittests
