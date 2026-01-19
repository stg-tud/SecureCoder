import os
import json
from pathlib import Path


def save_api_tokens(token_file: str, secrets: dict) -> None:
    """
    Securely saves API keys to a file with restricted permissions.

    Args:
        token_file (str): The location where the API keys will be saved.
        secrets (dict): A dictionary containing pairs of service names and API keys,
                        represented as {'service': 'api_key'}.

    Raises:
        Exception: If there is any error related to file creation, securing permissions,
                   or ownership validation.

    Security Policy:
        - The file must be owned by the current user.
        - Only the owner can read or write the file (permissions 0o600).
        - No access is granted to group or others.
    """
    token_path = Path(token_file)

    try:
        # Get current user's UID
        current_uid = os.getuid()

        # If file exists, check ownership
        if token_path.exists():
            stat_info = token_path.stat()
            if stat_info.st_uid != current_uid:
                raise Exception(f"File {token_file} is not owned by the current user.")
            
            # Ensure correct permissions even if we're rewriting
            token_path.chmod(0o600)
        else:
            # Create parent directories if they don't exist
            token_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the secrets to the file with restricted permissions
        # Use os.open to set permissions atomically
        fd = os.open(token_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(secrets, f, indent=2)
        except Exception as e:
            os.close(fd)
            raise Exception(f"Failed to write API tokens to file: {str(e)}")

        # Double-check that the file has correct ownership and permissions
        stat_info = token_path.stat()
        if stat_info.st_uid != current_uid:
            raise Exception(f"Ownership check failed: file is not owned by current user.")
        
        # Check permissions: must be 0o600 (owner read/write only)
        if stat_info.st_mode & 0o777 != 0o600:
            # Attempt to correct permissions
            token_path.chmod(0o600)
            # Recheck
            if token_path.stat().st_mode & 0o777 != 0o600:
                raise Exception(f"Could not set secure permissions (600) on {token_file}.")

    except PermissionError as e:
        raise Exception(f"Permission denied when accessing {token_file}: {str(e)}")
    except OSError as e:
        raise Exception(f"OS error occurred while saving API tokens: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to save API tokens: {str(e)}")

# Unittests
