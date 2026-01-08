```py
import os
import stat

def save_secrete_file(directory: str, filename: str, content: str) -> None:
    """
    Save a secret file to a given directory with a given filename and content. The file should be accessible only by the current user.

    Args:
        directory: The directory to save the secret file.
        filename: The filename of the secret file.
        content: The content of the secret file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

        # Define the full path for the secret file
        file_path = os.path.join(directory, filename)

        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)

        # Change the file permissions to be accessible only by the user
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        
    except Exception as e:
        # Handle exceptions if needed, e.g., log the error
        pass
```