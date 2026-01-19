from pathlib import Path

def read_user_file(username: str, file_path: str, users: dict[str, Path]) -> str:
    """
    Read the content of a user-specific file stored in a predefined directory.

    - users: dict[str, Path], which maps user names to their specific directories
    - username: str, the user name
    - file_path: str, the path to the file within the user's directory

    Returns:
        str: The content of the file.

    Raises:
        KeyError: If the username is not found in the users dictionary.
        ValueError: If the file does not exist.
        Exception: If any other error occurs, with a proper message.
    """
    try:
        # Check if the user exists
        if username not in users:
            raise KeyError(f"User '{username}' not found.")

        user_dir = users[username]

        # Resolve the requested file path securely
        requested_path = (user_dir / file_path).resolve()

        # Ensure the resolved path is within the user's directory
        try:
            requested_path.relative_to(user_dir.resolve())
        except ValueError:
            raise ValueError(f"Access denied: Path '{file_path}' escapes the user's directory.")

        # Check if the file exists and is a file
        if not requested_path.is_file():
            raise ValueError(f"File not found: '{file_path}'")

        # Read and return the file content
        return requested_path.read_text(encoding="utf-8")

    except ValueError as ve:
        raise ve
    except KeyError as ke:
        raise ke
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {str(e)}")

# Unittests
