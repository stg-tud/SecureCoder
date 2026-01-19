from pathlib import Path

def get_user_data(uid: str, filepath: str, user_record: dict[str, Path]) -> Path:
    """
    Retrieve the absolute path to a requested data file within a user's root directory.

    Args:
        uid: str, the unique identifier for the user.
        filepath: str, the path of the data file requested, relative to the user's root directory.
        user_record: dict[str, Path], maps user IDs to their root directories.

    Returns:
        Path: The absolute path to the requested file.

    Raises:
        KeyError: If the user ID is not in user_record.
        FileNotFoundError: If the specified file does not exist.
        Exception: For any other issues, with a detailed message.
    """
    try:
        # Step 1: Verify user exists
        if uid not in user_record:
            raise KeyError(f"User ID '{uid}' not found in user records.")

        user_root = user_record[uid]

        # Step 2: Resolve the requested file path relative to the user's root
        requested_path = (user_root / filepath).resolve()

        # Step 3: Security check - ensure the resolved path is within the user's root directory
        try:
            requested_path.relative_to(user_root.resolve())
        except ValueError:
            raise Exception(f"Access denied: attempted path traversal detected for user '{uid}' with file '{filepath}'.")

        # Step 4: Verify that the file actually exists
        if not requested_path.exists():
            raise FileNotFoundError(f"File not found: '{requested_path}'")

        return requested_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Re-raise known exceptions; wrap unexpected ones with context
        raise Exception(f"An error occurred while retrieving data for user '{uid}': {str(e)}") from e

# Unittests
