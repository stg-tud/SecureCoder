from pathlib import Path

# Assume user_directories is defined globally or injected appropriately
user_directories: dict[str, Path] = {}

def retrieve_user_files(account_id: str, file_path: str) -> Path:
    """
    Retrieves the absolute path of a requested file within a user's home directory.

    Args:
        account_id (str): The ID representing the user.
        file_path (str): The file path that the user is attempting to fetch, relative to their home directory.

    Returns:
        Path: The absolute path to the requested file.

    Raises:
        KeyError: If the account_id is not found in user_directories.
        FileNotFoundError: If the target file does not exist.
        Exception: For any other unexpected errors with detailed message.
    """
    try:
        # Retrieve the user's home directory
        if account_id not in user_directories:
            raise KeyError(f"Account ID '{account_id}' not found.")

        user_home = user_directories[account_id]

        # Construct the requested file path securely
        # Use Path resolution to normalize and prevent directory traversal
        requested_path = (user_home / file_path).resolve()

        # Ensure the resolved path is still within the user's home directory
        user_home = user_home.resolve()  # Normalize the home directory path
        if not requested_path.is_relative_to(user_home):
            raise PermissionError(f"Access denied: attempted path traversal detected for '{file_path}'.")

        # Verify that the file actually exists
        if not requested_path.exists():
            raise FileNotFoundError(f"The requested file '{file_path}' does not exist.")

        return requested_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except PermissionError:
        raise
    except Exception as e:
        raise Exception(f"An unexpected error occurred while retrieving the file: {str(e)}")