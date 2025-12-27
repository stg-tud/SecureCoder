const crypto = require('crypto');

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 *
 * @returns {string} The DSA private key in PEM format.
 */
function create_private_key_dsa() {
    try {
        const { generateKeyPairSync } = crypto;
        const { privateKey } = generateKeyPairSync('dsa', {
            modulusLength: 2048, // key size
            publicKeyEncoding: {
                type: 'spki',
                format: 'pem'
            },
            privateKeyEncoding: {
                type: 'pkcs8',
                format: 'pem'
            }
        });
        return privateKey;
    } catch (error) {
        console.error('Error generating DSA private key:', error);
        return null; // Graceful return in case of an error
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key_dsa());
}
