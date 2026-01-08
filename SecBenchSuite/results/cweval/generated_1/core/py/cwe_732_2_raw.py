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
        
        # Construct the full path of the file
        file_path = os.path.join(directory, filename)
        
        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)
        
        # Change the file permissions to make it accessible only by the current user
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
    except Exception as e:
        # Handling exceptions gracefully
        print(f"An error occurred while saving the secret file: {e}")
```