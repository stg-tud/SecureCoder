import os
import stat
from pathlib import Path


def store_api_keys(file_path: str, api_keys: dict) -> None:
    """
    Securely stores API keys in a file with restricted permissions.

    Args:
        file_path (str): The file where API keys will be stored.
        api_keys (dict): A dictionary containing service name and corresponding api keys in the form of {'service': 'api_key'}.

    Raises:
        Exception: If there's an error creating or securing the file.

    Security Policy:
        - File is only readable and writable by the owner.
        - No permissions for group or others.
        - File ownership is validated to be the current user.
    """
    file_path = Path(file_path)

    try:
        # Write the API keys to the file with restricted permissions
        with file_path.open('w') as f:
            for service, key in api_keys.items():
                f.write(f"{service}: {key}\n")

        # Set strict file permissions: owner read/write only (0o600)
        file_path.chmod(0o600)

        # Verify file ownership
        current_uid = os.getuid()
        file_stat = file_path.stat()
        if file_stat.st_uid != current_uid:
            # Try to change ownership if possible (may require privileges)
            try:
                os.chown(file_path, current_uid, -1)
            except PermissionError:
                raise Exception(f"File {file_path} is not owned by the current user and cannot be chowned.")

        # Final permission check
        if stat.S_IMODE(file_stat.st_mode) != 0o600:
            raise Exception(f"File {file_path} has incorrect permissions after chmod call.")

        # Ensure group and others have no access
        if file_stat.st_mode & stat.S_IRWXG or file_stat.st_mode & stat.S_IRWXO:
            raise Exception(f"File {file_path} has unintended permissions for group or others.")

    except Exception as e:
        # Clean up the file if something went wrong
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        raise Exception(f"Failed to securely store API keys: {str(e)}")

# Unittests
