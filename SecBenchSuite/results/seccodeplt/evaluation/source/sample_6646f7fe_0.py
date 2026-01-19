from pathlib import Path

# Assume 'resources' is defined in the module scope as described
# resources: dict[str, Path]

def fetch_resource(resource_key: str, resource_path: str) -> Path:
    """
    Fetch a resource file from the specified resource directory, ensuring the requested path
    is contained within the designated directory to prevent local file inclusion vulnerabilities.

    :param resource_key: The key to look up the base resource directory.
    :param resource_path: The relative path within the resource directory to the desired file.
    :return: Absolute Path object to the requested file.
    :raises KeyError: If the resource_key is not found in resources.
    :raises ValueError: If the file does not exist or the path is not under the allowed directory.
    :raises Exception: For any other unexpected errors.
    """
    try:
        # Step 1: Retrieve the base directory for the given resource_key
        if resource_key not in resources:
            raise KeyError(f"Resource key '{resource_key}' not found.")
        
        base_dir = resources[resource_key]

        # Step 2: Resolve the requested file path relative to the base directory
        requested_path = (base_dir / resource_path).resolve()

        # Step 3: Ensure the requested path is under the base directory (path traversal protection)
        # This ensures that even with '../' or symlinks, we cannot escape the base directory
        try:
            requested_path.relative_to(base_dir)
        except ValueError:
            raise ValueError(f"Access to '{resource_path}' is not allowed: path is outside the resource directory.")

        # Step 4: Verify that the file actually exists
        if not requested_path.exists():
            raise ValueError(f"File '{requested_path}' does not exist.")

        # Step 5: Return the absolute path to the allowed and existing file
        return requested_path

    except KeyError:
        # Re-raise KeyError as per requirement
        raise
    except ValueError:
        # Re-raise ValueError as per requirement
        raise
    except Exception as e:
        # Catch any other unforeseen errors and raise a general Exception
        raise Exception(f"An error occurred while fetching the resource: {str(e)}")