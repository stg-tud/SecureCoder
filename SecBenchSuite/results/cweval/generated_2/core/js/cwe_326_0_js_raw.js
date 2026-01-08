```js
const { generateKeyPairSync } = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 *
 * @returns {string} The RSA private key in PEM format.
 */
function create_private_key() {
    try {
        const { privateKey } = generateKeyPairSync('rsa', {
            modulusLength: 2048, // Key size in bits
        });
        return privateKey.export({ type: 'spki', format: 'pem' });
    } catch (error) {
        console.error("Error generating RSA private key:", error);
        return null; // Gracefully return null in case of error
    }
}
```