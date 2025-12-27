/**
 * Hash the given certificate securely and return the hash as a hexadecimal string.
 *
 *
 * @param {string} cert - The certificate to be hashed.
 * @returns {string} The securely hashed certificate as a hexadecimal string.
 */
function hash_certificate(cert) {
    const crypto = require('crypto');
    
    // Create a hash using SHA-256
    const hash = crypto.createHash('sha256');
    
    // Update the hash with the certificate string
    hash.update(cert);
    
    // Return the hash as a hexadecimal string
    return hash.digest('hex');
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length === 0) {
        console.error("Usage: node script.js <certificate>");
        process.exit(1);
    }
    const cert = args[0];
    console.log(hash_certificate(cert));
}
