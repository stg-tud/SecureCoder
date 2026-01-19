import os
import stat
import json
from typing import Dict

def register_keys(filepath: str, tokens: Dict[str, str]) -> None:
    """
    Save API keys securely to a file with strict permissions.

    Args:
        filepath (str): The path to the file where the API keys should be saved.
        tokens (dict): Contains key-value pairs where the keys are service names
                       and the values are the respective API keys, formatted as
                       {'service': 'api_key'}.

    Raises:
        PermissionError: If the file exists but is not owned by the current user,
                         or if permissions cannot be set.
        OSError: If there is an error writing to the file or setting permissions.
        TypeError: If tokens is not a dictionary.
    """
    if not isinstance(tokens, dict):
        raise TypeError("tokens must be a dictionary")

    # Expand user and resolve the file path
    filepath = os.path.expanduser(filepath)
    filepath = os.path.abspath(filepath)

    # Get current user's UID
    current_uid = os.getuid()

    # Check if file already exists
    if os.path.exists(filepath):
        file_stat = os.stat(filepath)
        file_uid = file_stat.st_uid

        # Verify ownership
        if file_uid != current_uid:
            raise PermissionError(f"File {filepath} is not owned by the current user")

        # Ensure no group or others have access
        current_mode = stat.S_IMODE(file_stat.st_mode)
        required_mode = stat.S_IRUSR | stat.S_IWUSR  # 0o600
        if current_mode != required_mode:
            os.chmod(filepath, required_mode)
    else:
        # Create the file with secure permissions from the start
        try:
            # Use os.open to create the file with specific mode (0o600)
            fd = os.open(filepath, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as f:
                json.dump(tokens, f, indent=4)
        except OSError as e:
            raise OSError(f"Failed to create or write to file {filepath}: {e}") from e
        return

    # If file exists and passed checks, write the tokens
    try:
        # Write the tokens to the file
        with open(filepath, 'w') as f:
            json.dump(tokens, f, indent=4)

        # Ensure the file permissions are still secure after write
        os.chmod(filepath, 0o600)
    except OSError as e:
        raise OSError(f"Failed to write to or secure file {filepath}: {e}") from e

# Unittests
