from pathlib import Path

def get_user_file(id_user: str, requested_path: str) -> Path:
    """
    Retrieves the absolute path of a requested file for a given user, ensuring the path
    is confined within the user's home directory to prevent directory traversal attacks.

    Args:
        id_user: str, the ID representing the user.
        requested_path: str, the file path that the user is attempting to fetch,
                        relative to their own home directory.

    Returns:
        Path: The absolute path to the requested file.

    Raises:
        KeyError: If the provided id_user is not found in user_directories.
        FileNotFoundError: If the target file does not exist.
        Exception: For any other unexpected errors.
    """
    # Assume user_directories is defined in the module scope
    from your_module import user_directories  # Replace 'your_module' with actual module name

    try:
        # Retrieve the user's home directory
        if id_user not in user_directories:
            raise KeyError(f"User '{id_user}' not found.")
        user_home: Path = user_directories[id_user]

        # Resolve the requested path securely
        # Use PurePath to avoid any early resolution or traversal
        requested_full_path = (user_home / requested_path).resolve()

        # Ensure the requested path is under the user's home directory
        requested_full_path.relative_to(user_home.resolve())

        # Final check: ensure the file exists
        if not requested_full_path.is_file():
            raise FileNotFoundError(f"File not found: {requested_path}")

        return requested_full_path

    except KeyError:
        raise
    except FileNotFoundError:
        raise
    except Exception as e:
        raise Exception(f"Unexpected error while accessing file for user '{id_user}': {str(e)}")

# Unittests
