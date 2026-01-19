from pathlib import Path

def fetch_user_data(user_id: str, relative_path: str, users: dict[str, Path]) -> str:
    """
    Read the contents of a file located in a user's designated folder.

    Args:
        user_id: str, specifying the name of the user
        relative_path: str, providing the relative path to the user's file within their directory
        users: dict[str, Path], mapping user names to their respective root directories

    Returns:
        The string contents of the requested file

    Raises:
        KeyError: if the user_id isn't found in the users mapping
        ValueError: if the specified file is missing
        Exception: for any other issues (e.g., permission errors, I/O problems)
    """
    # Check if user exists
    if user_id not in users:
        raise KeyError(f"User '{user_id}' not found")

    user_root = users[user_id]

    # Resolve the requested file path
    try:
        # Construct the file path
        file_path = (user_root / relative_path).resolve()

        # Construct the user root path and resolve it to compare
        user_root_resolved = user_root.resolve()

        # Security check: ensure the file_path is within the user's directory
        # This prevents directory traversal attacks (e.g., '../../../etc/passwd')
        if not file_path.is_relative_to(user_root_resolved):
            raise ValueError(f"Access denied: path '{relative_path}' attempts to traverse outside user directory")

        # Check if file exists and is a file
        if not file_path.exists():
            raise ValueError(f"File not found: '{relative_path}'")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: '{relative_path}'")

        # Read and return file contents
        return file_path.read_text(encoding='utf-8')

    except PermissionError as e:
        raise Exception(f"Permission denied when accessing file: {e}")
    except OSError as e:
        raise Exception(f"Error reading file: {e}")