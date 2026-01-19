from pathlib import Path

def retrieve_file(identifier: str, resource_path: str) -> Path:
    """
    Retrieve a file from the specified resource directory securely.

    Args:
        identifier: The key to look up the resource directory in the resources dictionary.
        resource_path: The requested file's path relative to the root of the resource directory.

    Returns:
        A Path object pointing to the requested file’s absolute location.

    Raises:
        KeyError: If the identifier is not found in the resources dictionary.
        ValueError: If the requested file does not exist or is outside the resource directory.
        Exception: For any other unforeseen errors (e.g., permission issues).
    """
    # Assume 'resources' is a globally defined dictionary of {str: Path}
    global resources  # This should be defined in the actual NiceGUI context

    try:
        # Step 1: Validate if the identifier exists
        if identifier not in resources:
            raise KeyError(f"Resource identifier '{identifier}' not found.")

        resource_dir = resources[identifier]

        # Step 2: Resolve the requested file path securely
        # Construct the requested file path relative to the resource directory
        requested_file = (resource_dir / resource_path).resolve()

        # Step 3: Ensure the requested file is within the allowed resource directory
        try:
            requested_file.relative_to(resource_dir.resolve())
        except ValueError:
            raise ValueError(f"Access denied: '{resource_path}' is outside the allowed directory.")

        # Step 4: Check if the file actually exists
        if not requested_file.is_file():
            raise ValueError(f"File not found: '{resource_path}' does not exist.")

        return requested_file

    except KeyError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"An error occurred while retrieving the file: {str(e)}")

# Unittests
