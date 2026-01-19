from pathlib import Path

user_directories: dict[str, Path] = {}

def retrieve_file_for_user(user_token: str, document_path: str) -> Path:
    """
    Retrieves the absolute path of a requested file for a given user, ensuring the path
    remains confined within the user's home directory to prevent directory traversal attacks.

    Args:
        user_token: str, the ID representing the user.
        document_path: str, the file path the user is attempting to fetch, relative to their home directory.

    Returns:
        Path: The absolute path to the requested file.

    Raises:
        KeyError: If the user_token is not found in user_directories.
        FileNotFoundError: If the target file does not exist.
        Exception: For any other unexpected errors with detailed messages.
    """
    try:
        # Retrieve the user's home directory
        if user_token not in user_directories:
            raise KeyError(f"User '{user_token}' not found.")

        user_home = user_directories[user_token]

        # Resolve the requested path securely
        requested_path = (user_home / document_path).resolve()

        # Ensure the requested path is within the user's home directory
        requested_path.relative_to(user_home)

        # Check if the file actually exists
        if not requested_path.is_file():
            raise FileNotFoundError(f"File not found: {requested_path}")

        return requested_path

    except KeyError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while retrieving the file: {str(e)}")