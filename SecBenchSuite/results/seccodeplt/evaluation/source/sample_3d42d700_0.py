from pathlib import Path


def get_user_file(users: dict[str, Path], person_name: str, path_to_file: str) -> str:
    """
    Reads the contents of a file located in a user's designated folder.

    Args:
        users: dict mapping user names to their respective root directories
        person游戏副本Name: str, specifying the name of the user
        path_to_file: str, providing the relative path to the user's file within their directory

    Returns:
        The string contents of the requested file

    Raises:
        KeyError: if the person_name isn't found in the users mapping
        ValueError: if the specified file is missing
        Exception: for any other issues (e.g., IO errors, permission issues)
    """
    # Check if the user exists
    if person_name not in users:
        raise KeyError(f"User '{person_name}' not found")

    user_dir = users[person_name]

    # Validate and construct the file path
    try:
        # Use Path to handle path traversal safely
        requested_path = (user_dir / path_to_file).resolve()

        # Ensure the resolved path is within the user's directory
        requested_path.relative_to(user_dir.resolve())

        # Read and return file contents
        if not requested_path.is_file():
            raise ValueError(f"File not found: {path_to_file}")

        return requested_path.read_text()

    except ValueError as ve:
        # Re-raise ValueError if file not found or path outside user dir
        if "relative path" in str(ve):
            raise ValueError(f"Invalid file path: '{path_to_file}' attempts path traversal")
        raise
    except Exception as e:
        # Wrap other exceptions (e.g., permission errors, read issues)
        raise Exception(f"Error reading file: {e}")