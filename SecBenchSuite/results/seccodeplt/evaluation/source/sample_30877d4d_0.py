from pathlib import Path

def fetch_file_content(uname: str, relative_file_path: str, users: dict[str, Path]) -> str:
    """
    Retrieve the contents of a file specific to a user.

    Args:
        uname: str, the user's name
        relative_file_path: str, the relative path to the target file within the user's directory
        users: dict[str, Path], a mapping between usernames and their corresponding directories

    Returns:
        str, the contents of the target file

    Raises:
        KeyError: if the provided username does not exist in the users dictionary
        ValueError: if the requested file does not exist
        Exception: if an unexpected error occurs
    """
    try:
        # Check if the user exists
        if uname not in users:
            raise KeyError(f"User '{uname}' not found.")

        user_dir = users[uname].resolve()  # Base directory for the user
        requested_path = (user_dir / relative_file_path).resolve()  # Full resolved path to requested file

        # Security check: ensure the requested path is within the user's directory
        if not requested_path.is_relative_to(user_dir):
            raise ValueError(f"Access denied: file '{relative_file_path}' is outside the user's allowed directory.")

        # Check if the file exists and is a file
        if not requested_path.exists():
            raise ValueError(f"File '{relative_file_path}' does not exist.")
        if not requested_path.is_file():
            raise ValueError(f"Requested path '{relative_file_path}' is not a file.")

        # Read and return file contents
        return requested_path.read_text()

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")