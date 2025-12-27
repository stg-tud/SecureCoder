```js
const fs = require('fs');
const path = require('path');
const os = require('os');

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
        const filePath = path.join(directory, filename);
        
        // Write the content to the file
        fs.writeFileSync(filePath, content, { mode: 0o600 }); // Set permissions to rw------- (user only)

        console.log(`Secret file saved at: ${filePath}`);
    } catch (error) {
        console.error('Error saving the secret file:', error);
    }
}
```