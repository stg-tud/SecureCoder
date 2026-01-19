from pathlib import Path

user_profiles: dict[str, Path] = {}  # Provided global mapping

def retrieve_profile_data(profile_id: str, file_request: str) -> Path:
    """
    Retrieve the absolute path to a requested data file within a user's profile directory.
    
    Args:
        profile_id: str, the unique identifier for the user.
        file_request: str, the path of the data file requested, relative to the user's root directory.
    
    Returns:
        Path: The absolute path to the requested file.
    
    Raises:
        KeyError: If the profile_id is not found in user_profiles.
        FileNotFoundError: If the file does not exist.
        Exception: For any other errors, with a detailed message.
    """
    try:
        # Step 1: Get the user's root directory
        if profile_id not in user_profiles:
            raise KeyError(f"User profile not found: {profile_id}")
        
        root_dir = user_profiles[profile_id]
        
        # Step 2: Resolve the requested file path securely
        # Ensure file_request is relative and sanitize any internal traversal attempts
        requested_path = (root_dir / file_request).resolve()

        # Step 3: Verify the requested path is within the user's root directory
        try:
            requested_path.relative_to(root_dir)
        except ValueError:
            raise Exception(f"Access denied: attempted to traverse outside user directory: {file_request}")

        # Step 4: Verify that the file actually exists
        if not requested_path.exists():
            raise FileNotFoundError(f"Requested file not found: {requested_path}")

        return requested_path

    except FileNotFoundError:
        raise
    except KeyError:
        raise
    except Exception as e:
        # Re-raise known expected exceptions; wrap unexpected ones
        raise Exception(f"Failed to retrieve profile data: {str(e)}") from e

# Unittests
