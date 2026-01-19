from pathlib import Path

def load_user_file(
    account_name: str,
    relative_file_path: str,
    users: dict[str, Path],
) -> str:
    """
    Open and read a specific file associated with a user.

    - account_name: str, a string representing the user’s name
    - relative_file_path: str, a string representing the path to the file
      relative to the user's directory
    - users: dict[str, Path], mapping user names to their home directories

    Returns:
        str: the content of the file as a string

    Raises:
        KeyError: if the account_name is not found in users
        ValueError: if the requested file does not exist or path is invalid
        Exception: for any other unforeseen errors
    """
    try:
        # Verify user exists
        if account_name not in users:
            raise KeyError(f"User '{account_name}' not found.")

        user_home: Path = users[account_name]

        # Ensure user_home is a directory and exists
        if not user_home.exists():
            raise ValueError(f"User home directory does not exist: {user_home}")
        if not user_home.is_dir():
            raise ValueError(f"User home path is not a directory: {user_home}")

        # Resolve the requested file path securely
        requested_path = (user_home / relative_file_path).resolve()

        # Security check: Ensure the resolved path is within the user's home directory
        try:
            requested_path.relative_to(user_home)
        except ValueError:
            raise ValueError(f"Access denied: Path '{relative_file_path}' attempts to escape user directory.")

        # Check if file exists and is a file
        if not requested_path.exists():
            raise ValueError(f"File not found: {requested_path}")
        if not requested_path.is_file():
            raise ValueError(f"Requested path is not a file: {requested_path}")

        # Read and return file content
        return requested_path.read_text(encoding="utf-8")

    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Unexpected error while loading file: {e}") from e