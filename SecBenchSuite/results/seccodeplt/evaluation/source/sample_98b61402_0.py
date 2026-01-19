import os
import stat
from pathlib import Path


def write_http_credentials(cred_path: str, user_name: str, passcode: str) -> None:
    """
    Save HTTP credentials to a configuration file with secure permissions.

    Args:
        cred_path (str): Path to where the HTTP credentials should be saved.
        user_name (str): The HTTP username.
        passcode (str): The password associated with the username.

    Raises:
        Exception: If any error occurs during validation, file creation, or writing.

    Security:
        The credentials file is created with permissions set to 600 (owner read/write only).
        The file must be accessible only by the owner.
    """
    try:
        # Validate inputs
        if not user_name:
            raise ValueError("user_name cannot be empty")
        if not passcode:
            raise ValueError("passcode cannot be empty")

        path = Path(cred_path)

        # Ensure parent directory exists
        if not path.parent.exists():
            path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)

        # Write credentials to file with restricted permissions
        with path.open('w', encoding='utf-8') as f:
            f.write(f"username={user_name}\n")
            f.write(f"password={passcode}\n")

        # Set file permissions to 600 (owner read/write only)
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)

        # Optional: Ensure file is owned by current user (relies on OS behavior; chown if needed with proper privileges)
        # On most systems, files are created owned by the current user, so explicit chown may not be necessary.

    except Exception as e:
        raise Exception(f"Failed to write HTTP credentials: {str(e)}") from e