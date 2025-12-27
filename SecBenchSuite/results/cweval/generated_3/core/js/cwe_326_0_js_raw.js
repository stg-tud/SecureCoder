```js
const crypto = require('crypto');

/**
 * Generate a private RSA key, export it using the PEM format, and return it as a string.
 *
 *
 * @returns {string} The RSA private key in PEM format.
 */
function create_private_key() {
    try {
        const { privateKey } = crypto.generateKeyPairSync('rsa', {
            modulusLength: 2048, // Key size
        });
        const pem = privateKey.export({
            type: 'pkcs8',
            format: 'pem'
        });
        return pem;
    } catch (error) {
        console.error('Error generating private key:', error);
        return '';
    }
}
```