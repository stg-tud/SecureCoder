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
            modulusLength: 2048, // Length of the key in bits
        });
        return privateKey.export({ format: 'pem', type: 'pkcs1' });
    } catch (error) {
        console.error('Error generating RSA key:', error);
        return null; // Gracefully return null on error
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key());
}
