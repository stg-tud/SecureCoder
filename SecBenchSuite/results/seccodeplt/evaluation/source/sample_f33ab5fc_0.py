from pathlib import Path

# Assume this is defined elsewhere in the module
# user_directories: dict[str, Path] = { ... }

def get_user_file(usr_id: str, file_path: str) -> Path:
    """
    Retrieve the actual path to a user's file, ensuring the path stays within the user's root directory.

    Args:
        usr_id (str): User-specific identifier.
        file_path (str): The relative path of the file within the user's directory.

    Returns:
        Path: The absolute Path object pointing to the requested file.

    Raises:
        KeyError: If the usr_id is not found in user_directories.
        FileNotFoundError: If the resolved file does not exist.
        Exception: For any other issues (e.g., permission errors, invalid paths).
    """
    # Retrieve the user's root directory
    if usr_id not in user_directories:
        raise KeyError(f"User ID '{usr_id}' not found.")

    user_root = user_directories[usr_id]

    # Validate and construct the full intended path
    try:
        # Resolve the relative path securely
        requested_path = (user_root / file_path).resolve()

        # Ensure the path is inside the user's root directory (security check)
        requested_path.relative_to(user_root)
    except ValueError as ve:
        raise Exception(f"Invalid path traversal attempt: '{file_path}' is outside the user's directory.") from ve
    except Exception as e:
        raise Exception(f"Error processing file path: {e}") from e

    # Check if the file actually exists
    if not requested_path.is_file():
        raise FileNotFoundError(f"The file '{file_path}' was not found in user '{usr_id}' directory.")

    return requested_path