from pathlib import Path


def load_user_file(uname: str, filepath: str, users: dict[str, Path]) -> str:
    """
    Retrieve the contents of a file specific to a user.

    - uname: str, the user's name
    - filepath: str, the relative path to the target file within the user's directory
    - users: dict[str, Path], a mapping between usernames and their corresponding directories

    Returns:
        str, the contents of the target file

    Raises:
        KeyError: if the provided username does not exist in the users dictionary
        ValueError: if the requested file does not exist or resolves outside the user's directory
        Exception: if an unexpected error occurs
    """
    try:
        # Check if user exists
        if uname not in users:
            raise KeyError(f"User '{uname}' not found.")

        user_dir: Path = users[uname]

        # Resolve the requested file path securely
        requested_path = (user_dir / filepath).resolve()
        user_dir = user_dir.resolve()

        # Ensure the requested path is within the user's directory (path traversal defense)
        if not requested_path.is_relative_to(user_dir):
            raise ValueError(f"Access denied: File path '{filepath}' attempts to access outside {user_dir}")

        # Check if file exists and is a file
        if not requested_path.exists():
            raise ValueError(f"File not found: {filepath}")
        if not requested_path.is_file():
            raise ValueError(f"Requested path is not a file: {filepath}")

        # Return file contents
        return requested_path.read_text()

    except (KeyError, ValueError) as e:
        raise e
    except Exception as e:
        raise Exception(f"An unexpected error occurred while loading file for user '{uname}': {e}")

# Unittests
