```js
const fs = require('fs');
const path = require('path');

/**
 * Save a secret file to a given directory with a given filename and content.
 * The file should be accessible only by the current user.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 * @param {string} content - The content of the secret file.
 */
function saveSecretFile(directory, filename, content) {
    try {
        // Ensure the directory exists
        if (!fs.existsSync(directory)) {
            fs.mkdirSync(directory, { recursive: true });
        }

        const filePath = path.join(directory, filename);

        // Write content to the file
        fs.writeFileSync(filePath, content);

        // Change the file permissions to be accessible only by the current user
        fs.chmodSync(filePath, 0o600); // rw------- permissions
    } catch (error) {
        console.error('Error saving secret file:', error);
    }
}
```