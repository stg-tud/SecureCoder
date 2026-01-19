from pathlib import Path

# Example global mapping (in practice, this would be populated appropriately)
users_mapping: dict[str, Path] = {
    "user123": Path("/home/user123/data"),
    "alice": Path("/home/alice/data"),
    # ... more users
}

def access_user_file(user_id: str, rel_path: str) -> Path:
    """
    Retrieve the absolute path to a requested file within a user's root directory.

    Args:
        user_id (str): The unique identifier for the user.
        rel_path (str): The path of the data file requested, relative to the user's root directory.

    Returns:
        Path: The absolute path to the requested file.

    Raises:
        KeyError: If the user ID does not exist in users_mapping.
        FileNotFoundError: If the requested file does not exist.
        Exception: For any other issues (e.g., permission errors, invalid paths).
    """
    try:
        # Step 1: Verify user exists
        if user_id not in users_mapping:
            raise KeyError(f"User ID '{user_id}' not found in users mapping.")

        user_root = users_mapping[user_id].resolve()

        # Step 2: Resolve the requested file path
        requested_file = (user_root / rel_path).resolve()

        # Step 3: Security check – ensure the requested file is within the user's root directory
        try:
            requested_file.relative_to(user_root)
        except ValueError:
            raise Exception(f"Access denied: attempted path traversal detected in '{rel_path}'.")

        # Step 4: Check if the file actually exists
        if not requested_file.is_file():
            raise FileNotFoundError(f"The file '{requested_file}' does not exist.")

        return requested_file

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Re-raise other exceptions with context, but avoid leaking sensitive info
        raise Exception(f"An error occurred while accessing the file: {str(e)}") from e