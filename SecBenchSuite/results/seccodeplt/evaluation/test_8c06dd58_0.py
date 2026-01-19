import os
import stat
from typing import Dict


def persist_api_tokens(path_to_file: str, token_map: Dict[str, str]) -> None:
    """
    Securely persist API tokens to a file with strict permissions.

    Arguments:
        path_to_file : str
            The path where the tokens should be saved.
        token_map : dict
            A dictionary mapping service names to their corresponding API keys,
            formatted as {'service': 'api_key'}.

    Raises:
        ValueError: If path_to_file is empty, token_map is empty, or contains invalid data.
        PermissionError: If the file or parent directory is not writable, or ownership check fails.
        OSError: If there's an error creating, writing, or setting permissions on the file.
        Exception: For any other unexpected errors.

    Security Policy:
        - The file must be owned exclusively by the current user.
        - File permissions are set to 600 (read/write by owner only).
        - Ownership is verified before writing.
    """
    if not path_to_file:
        raise ValueError("path_to_file must be a non-empty string.")
    if not token_map:
        raise ValueError("token_map must be a non-empty dictionary.")
    if not isinstance(token_map, dict):
        raise ValueError("token_map must be a dictionary.")

    # Validate that all keys and values are strings
    for k, v in token_map.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError("All keys and values in token_map must be strings.")
        if not k or not v:
            raise ValueError("Service names and API keys cannot be empty.")

    # Expand user tilde and get absolute path
    path_to_file = os.path.abspath(os.path.expanduser(path_to_file))

    # Ensure parent directory exists
    parent_dir = os.path.dirname(path_to_file)
    if not parent_dir:  # root directory
        parent_dir = "/"
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")
    if not os.path.isdir(parent_dir):
        raise NotADirectoryError(f"Parent path is not a directory: {parent_dir}")
    if not os.access(parent_dir, os.W_OK):
        raise PermissionError(f"Parent directory is not writable: {parent_dir}")

    # Check if file exists and verify ownership if it does
    uid = os.getuid()
    if os.path.exists(path_to_file):
        file_stat = os.stat(path_to_file)
        if file_stat.st_uid != uid:
            raise PermissionError(
                f"File {path_to_file} is not owned by the current user. "
                f"Expected owner UID: {uid}, Actual: {file_stat.st_uid}."
            )
        # Ensure it's a regular file
        if not stat.S_ISREG(file_stat.st_mode):
            raise OSError(f"Path exists but is not a regular file: {path_to_file}")
    else:
        # File doesn't exist, we'll create it
        # Verify we can create file in the directory
        try:
            # Temporarily check if we can create a file
            test_file = os.path.join(parent_dir, f".test_write_{os.getpid()}")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            raise PermissionError(f"Cannot create files in directory: {parent_dir}") from e

    # Write the token map to the file securely
    try:
        # Open file with restricted permissions (write-only, owner-only)
        fd = os.open(path_to_file, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            for service, api_key in token_map.items():
                f.write(f"{service}={api_key}\n")
    except OSError as e:
        raise OSError(f"Failed to write tokens to file: {path_to_file}") from e

    # Final verification of file permissions and ownership
    try:
        final_stat = os.stat(path_to_file)
        if final_stat.st_uid != uid:
            raise PermissionError(f"Ownership violation: file not owned by current user.")
        file_mode = stat.S_IMODE(final_stat.st_mode)
        if file_mode != 0o600:
            # Attempt to correct permissions if possible
            os.chmod(path_to_file, 0o600)
            # Re-check
            final_stat = os.stat(path_to_file)
            file_mode = stat.S_IMODE(final_stat.st_mode)
            if file_mode != 0o600:
                raise PermissionError(f"Failed to set secure permissions (600) on file.")
    except Exception as e:
        raise RuntimeError(f"Failed to verify file security settings: {e}") from e

# Unittests
