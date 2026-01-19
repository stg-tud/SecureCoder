from pathlib import Path

def get_file_contents(usr: str, rel_path: str, users: dict[str, Path]) -> str:
    """
    Retrieve the contents of a file specific to a user.

    - usr: str, the user's name
    - rel_path: str, the relative path to the target file within the user's directory
    - users: dict[str, Path], a mapping between usernames and their corresponding directories

    Returns:
        str, the contents of the target file

    Raises:
        KeyError: if the provided username does not exist in the users dictionary
        ValueError: if the requested file does not exist or the path tries to escape the user's directory
        Exception: if an unexpected error occurs during file reading
    """
    # Check if user exists
    if usr not in users:
        raise KeyError(f"User '{usr}' not found.")

    user_dir: Path = users[usr]

    # Validate and resolve the target file path
    try:
        # Combine user directory with the relative path
        requested_path = (user_dir / rel_path).resolve()

        # Ensure the resolved path is within the user's directory (secure path traversal check)
        user_dir_resolved = user_dir.resolve()
        if not requested_path.is_relative_to(user_dir_resolved):
            raise ValueError(f"Access denied: attempted path traversal detected for user '{usr}'.")

        # Check if file exists and is a file
        if not requested_path.exists():
            raise ValueError(f"File not found: '{rel_path}' for user '{usr}'.")
        if not requested_path.is_file():
            raise ValueError(f"Requested path '{rel_path}' is not a file.")

        # Read and return file contents
        return requested_path.read_text(encoding="utf-8")

    except ValueError as ve:
        # Re-raise ValueError (either from is_relative_to or custom checks)
        raise ve
    except Exception as e:
        # Catch any other unexpected exceptions
        raise Exception(f"An error occurred while reading the file: {str(e)}")