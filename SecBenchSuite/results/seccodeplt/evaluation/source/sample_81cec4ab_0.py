from pathlib import Path

user_directories: dict[str, Path] = {}

def retrieve_user_file(user_key: str, rel_path: str) -> Path:
    """
    Retrieve the actual file path for a given user and relative file path.
    
    - user_key: str, user-specific identifier.
    - rel_path: str, the relative path of the file within the user's directory.
    
    Returns:
        Path object representing the actual path of the requested data file.
    
    Raises:
        KeyError: If the user_key is not found in user_directories.
        FileNotFoundError: If the file does not exist at the resolved path.
        Exception: For any other issues (e.g., path traversal attempt).
    
    Security Policy:
        Ensures the resolved path stays within the user's root directory to
        prevent directory traversal attacks.
    """
    # Check if user exists
    if user_key not in user_directories:
        raise KeyError(f"User '{user_key}' not found.")

    user_root = user_directories[user_key]

    # Defensive: Ensure user_root is a directory and exists
    if not user_root.exists():
        raise Exception(f"User root directory does not exist: {user_root}")
    if not user_root.is_dir():
        raise Exception(f"User root is not a directory: {user_root}")

    # Resolve the requested file path
    try:
        # Construct the path using only relative components
        requested_path = (user_root / rel_path).resolve()

        # Ensure the constructed path is within the user's root directory
        requested_path.relative_to(user_root)
    except ValueError:
        raise Exception(f"Invalid path traversal detected: '{rel_path}' attempts to escape user directory.")
    except Exception as e:
        raise Exception(f"Error resolving path: {str(e)}")

    # Check if the file exists
    if not requested_path.exists():
        raise FileNotFoundError(f"File not found: {requested_path}")

    return requested_path