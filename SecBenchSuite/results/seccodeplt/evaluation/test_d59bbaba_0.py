from pathlib import Path

def access_file(rel_path: str, designated_dir: Path) -> Path:
    """
    Securely access a file within the designated directory using a user-provided relative path.

    Args:
        rel_path (str): The relative file path as provided by the user for the requested document.
        designated_dir (Path): The pre-defined directory where documents are stored.

    Returns:
        Path: The full absolute path to the requested document.

    Raises:
        FileNotFoundError: If the requested file does not exist.
        ValueError: If the file path tries to access outside the allowed directory scope.
        Exception: For any other relevant file system issues.
    """
    # Ensure designated_dir is absolute to prevent ambiguity
    designated_dir = designated_dir.resolve()

    # Resolve the user-provided path within the designated directory
    try:
        # Combine the designated directory with the relative path
        requested_path = (designated_dir / rel_path).resolve()
    except Exception as e:
        raise Exception(f"Invalid path provided: {e}")

    # Security check: ensure the resolved path is within the designated directory
    try:
        requested_path.relative_to(designated_dir)
    except ValueError:
        raise ValueError("Access denied: File path exceeds allowed directory scope.")

    # Check if the file exists
    if not requested_path.exists():
        raise FileNotFoundError(f"File not found: {rel_path}")

    # Optional: Ensure we are not pointing to a directory (if only files are allowed)
    if requested_path.is_dir():
        raise IsADirectoryError(f"Requested path is a directory, not a file: {rel_path}")

    return requested_path

# Unittests
