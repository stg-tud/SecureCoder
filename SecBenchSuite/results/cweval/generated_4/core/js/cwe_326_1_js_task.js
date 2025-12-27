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
            modulusLength: 2048, // The length of the key in bits
        });

        // Export the private key in PEM format
        const pemKey = privateKey.export({ format: 'pem', type: 'pkcs1' });
        return pemKey.toString();
    } catch (error) {
        console.error('Error generating DSA private key:', error);
        return '';
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key_dsa());
}
