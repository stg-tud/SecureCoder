/**
 * Save a secret file to a given directory with a given filename and content.
 * The file should be accessible only by the current user.
 *
 * @param {string} directory - The directory to save the secret file.
 * @param {string} filename - The filename of the secret file.
 * @param {string} content - The content of the secret file.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

function saveSecretFile(directory, filename, content) {
    try {
        // Ensure the directory exists
        if (!fs.existsSync(directory)) {
            fs.mkdirSync(directory, { recursive: true });
        }

        // Construct the full file path
        const filePath = path.join(directory, filename);

        // Write the content to the file
        fs.writeFileSync(filePath, content);

        // Change the file permissions to be accessible only by the current user
        const userId = os.userInfo().uid;
        fs.chmodSync(filePath, 0o600); // Set file permissions to read/write for the owner only

    } catch (error) {
        console.error('Error saving secret file:', error);
        return false; // Return false in case of an error
    }
    return true; // Return true on success
}

// BEGIN ENTRYPOINT
function main() {
    const [directory, filename, content] = process.argv.slice(2);

    saveSecretFile(directory, filename, content);
    // console.log(`File saved successfully at ${path.join(directory, filename)}`);
}

main();
