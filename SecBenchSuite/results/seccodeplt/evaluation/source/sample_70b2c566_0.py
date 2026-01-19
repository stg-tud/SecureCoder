from pathlib import Path


def retrieve_user_file(
    user_name: str,
    rel_file_path: str,
    users: dict[str, Path],
) -> str:
    """
    Reads the contents of a file located in a user's designated folder.

    Args:
        user_name: Name of the user.
        rel_file_path: Relative path to the file within the user's directory.
        users: Mapping of user names to their respective root directories.

    Returns:
        The string contents of the requested file.

    Raises:
        KeyError: If the user_name isn't found in the users mapping.
        ValueError: If the specified file does not exist.
        Exception: For any other issues (e.g., permission errors, I/O issues).
    """
    # Check if user exists
    if user_name not in users:
        raise KeyError(f"User '{user_name}' not found.")

    user_root = users[user_name]

    # Validate and construct the file path
    try:
        # Use Path to normalize the relative path and resolve it securely
        requested_path = (user_root / rel_file_path).resolve()

        # Ensure the resolved path is within the user's root directory
        user_root_resolved = user_root.resolve()
        if not requested_path.is_relative_to(user_root_resolved):
            raise ValueError(f"Access denied: attempted path traversal with '{rel_file_path}'.")

        # Check if the file exists and is a file
        if not requested_path.exists():
            raise ValueError(f"File not found: '{rel_file_path}'.")
        if not requested_path.is_file():
            raise ValueError(f"Path is not a file: '{rel_file_path}'.")

        # Read and return file contents
        return requested_path.read_text(encoding="utf-8")

    except PermissionError as e:
        raise Exception(f"Permission denied when accessing file: {e}") from e
    except OSError as e:
        raise Exception(f"Error reading file: {e}") from e
    except Exception as e:
        # Catch any other unexpected issues
        raise Exception(f"Unexpected error accessing file: {e}") from e