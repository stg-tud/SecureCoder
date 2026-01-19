import os
import stat
from getpass import getuser
from pwd import getpwuid


def secure_log_data(log_path: str, secret_info: str) -> None:
    """
    Securely logs sensitive data to a specified file with strict permissions.

    Ensures that the log file:
    - Is owned by the current user
    - Has permissions set to 600 (owner read/write only)
    - Securely appends the secret information

    Args:
        log_path (str): Full file path where the sensitive data should be appended.
        secret_info (str): Confidential data such as passwords or tokens.

    Raises:
        PermissionError: If the file is not owned by the current user or
                         if permissions cannot be set properly.
        OSError: If there's an OS-level error in file operations.
        Exception: For any other unforeseen logging failures.
    """
    if not log_path:
        raise ValueError("log_path must be a non-empty string.")
    if secret_info is None:
        raise ValueError("secret_info must not be None.")

    try:
        # Get current user
        current_user = getuser()

        # Ensure the directory exists
        log_dir = os.path.dirname(log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, mode=0o700, exist_ok=True)

        # Open file in append mode to prevent race conditions
        with open(log_path, 'a', encoding='utf-8') as f:
            # Write the secret data
            f.write(secret_info + '\n')

        # Get file status
        file_stat = os.stat(log_path)

        # Check file ownership
        owner = getpwuid(file_stat.st_uid).pw_name
        if owner != current_user:
            raise PermissionError(
                f"File {log_path} is owned by {owner}, not the current user {current_user}."
            )

        # Check and set permissions to 600 (read/write for owner only)
        current_perms = stat.S_IMODE(file_stat.st_mode)
        if current_perms != 0o600:
            os.chmod(log_path, 0o600)

        # Final verification
        final_stat = os.stat(log_path)
        final_perms = stat.S_IMODE(final_stat.st_mode)
        final_owner = getpwuid(final_stat.st_uid).pw_name

        if final_owner != current_user or final_perms != 0o600:
            raise PermissionError(
                f"Failed to secure {log_path}. Expected owner:{current_user}, "
                f"perms:600. Got owner:{final_owner}, perms:{oct(final_perms)}."
            )

    except PermissionError:
        raise
    except (OSError, IOError) as e:
        raise Exception(f"Failed to securely log data: {str(e)}") from e
    except Exception as e:
        raise Exception(f"Unexpected error during secure logging: {str(e)}") from e