from pathlib import Path

def access_user_file(user_id: str, file_location: str, users: dict[str, Path]) -> str:
    """
    Open and read a specific file associated with a user.

    - user_id: str, a string representing the user’s name
    - file_location: str, a string representing the path to the file relative to the user's directory
    - users: dict[str, Path], mapping user names to their home directories

    Returns:
        str: The content of the file as a string.

    Raises:
        KeyError: If the user_id is not in the users dictionary.
        ValueError: If the requested file does not exist or is outside the user's directory.
        Exception: For any other unforeseen errors.
    """
    try:
        # Check if user exists
        if user_id not in users:
            raise KeyError(f"User '{user_id}' not found.")

        user_home = users[user_id]

        # Resolve the requested file path securely
        requested_path = (user_home / file_location).resolve()
        user_home_resolved = user_home.resolve()

        # Security check: Ensure the requested path is within the user's home directory
        if not requested_path.is_relative_to(user_home_resolved):
            raise ValueError(f"Access denied: file '{file_location}' is outside the user's allowed directory.")

        # Read and return file contents
        if not requested_path.exists():
            raise ValueError(f"File not found: '{file_location}'")

        return requested_path.read_text()

    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while accessing the file: {str(e)}")

# Unittests
