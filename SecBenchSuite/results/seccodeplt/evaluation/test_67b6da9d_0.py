from pathlib import Path

def fetch_user_data(user_id: str, path: str, user_directories: dict[str, Path]) -> Path:
    """
    Fetches the real path of a user data file, ensuring the path is within the user's directory.

    Args:
        user_id: str, the ID of the user
        path: str, the path of the data file the user wants to access relative to the user's root directory
        user_directories: dict[str, Path], maps user IDs to their respective root directories

    Returns:
        Path: the real path of the data file

    Raises:
        KeyError: if the user_id is not found in user_directories
        FileNotFoundError: if the file does not exist
        Exception: if any other exception occurs, with an appropriate message
    """
    try:
        # Check if user_id exists in user_directories
        if user_id not in user_directories:
            raise KeyError(f"User ID '{user_id}' not found in user directories.")

        user_root = user_directories[user_id]
        requested_path = (user_root / path).resolve()

        # Security check: Ensure the resolved path is within the user's root directory
        user_root_resolved = user_root.resolve()
        if not requested_path.is_relative_to(user_root_resolved):
            raise Exception(f"Access denied: attempted to access path outside user directory: {path}")

        # Check if the file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: {requested_path}")

        return requested_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Re-raise other expected exceptions or wrap unexpected ones
        raise Exception(f"An error occurred while fetching user data: {str(e)}") from e

# Unittests
