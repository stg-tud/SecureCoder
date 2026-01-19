from pathlib import Path

# Assume user_directories is defined globally or injected appropriately
user_directories: dict[str, Path] = {}

def load_user_data(uid: str, file_path: str) -> Path:
    """
    Retrieve the actual path to a user's data file, ensuring the path stays within the user's root directory.

    Args:
        uid: str, user-specific identifier.
        file_path: str, the relative path of the file within the user's directory.

    Returns:
        Path object representing the actual path of the requested data file.

    Raises:
        KeyError: If the provided uid is not found in user_directories.
        FileNotFoundError: If the resulting file does not exist.
        Exception: For any other issues (e.g., security violations, I/O errors).
    """
    # Check if user exists
    if uid not in user_directories:
        raise KeyError(f"User with ID '{uid}' not found.")

    user_root = user_directories[uid]

    # Validate and construct secure path
    try:
        # Normalize the requested file path and resolve against user root
        requested_path = (user_root / file_path).resolve()

        # Security check: Ensure the resolved path is within the user's root directory
        user_root_resolved = user_root.resolve()
        if not requested_path.is_relative_to(user_root_resolved):
            raise Exception(f"Access denied: Path '{file_path}' attempts to escape user directory.")

        # Ensure the file exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: '{file_path}'")

        return requested_path

    except Exception as e:
        # Re-raise known errors, wrap unexpected ones
        if isinstance(e, (KeyError, FileNotFoundError)):
            raise
        raise Exception(f"Error accessing file: {str(e)}")