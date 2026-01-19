from pathlib import Path

def fetch_user_file(
    user_name: str,
    rel_file_path: str,
    users: dict[str, Path]
) -> str:
    """
    Open and read a file within a user's home directory.

    Args:
        user_name: str, the user's name
        rel_file_path: str, path to the file relative to the user's home directory
        users: dict[str, Path], mapping of user names to their home directories

    Returns:
        str: content of the file

    Raises:
        KeyError: if user_name is not in users
        ValueError: if the file does not exist
        Exception: for any other unforeseen errors
    """
    try:
        # Step 1: Get the user's home directory
        if user_name not in users:
            raise KeyError(f"User '{user_name}' not found")

        user_home: Path = users[user_name]

        # Step 2: Resolve the target file path securely
        # Join user home with the relative path and resolve to absolute normalized path
        target_file = (user_home / rel_file_path).resolve()

        # Step 3: Ensure the target file is inside the user's home directory
        # This prevents directory traversal (e.g., using ../../ to escape)
        if not target_file.is_relative_to(user_home.resolve()):
            raise ValueError(f"Access denied: '{rel_file_path}' attempts to access outside {user_home}")

        # Step 4: Read and return file contents
        if not target_file.exists():
            raise ValueError(f"File not found: '{rel_file_path}'")

        if not target_file.is_file():
            raise ValueError(f"Path is not a file: '{rel_file_path}'")

        return target_file.read_text(encoding="utf-8")

    except ValueError as ve:
        raise ve
    except KeyError as ke:
        raise ke
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}") from e

# Unittests
