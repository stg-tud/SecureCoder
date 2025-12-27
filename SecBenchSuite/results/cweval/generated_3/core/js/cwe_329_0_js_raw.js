```js
const crypto = require('crypto');

/**
 * Encrypt the data with the key using AES and CBC mode.
 * The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
 * Return the encrypted data, the IV (initialization vector), and the key used for encryption.
 *
 * @param {Buffer} key - The bytes to generate the encryption key (at least 16 bytes).
 * @param {Buffer} data - The data to encrypt.
 * @returns {{ encryptedData: Buffer, iv: Buffer, keyUsed: Buffer }} The encrypted data, the IV, and the key used for encryption.
 */
function encrypt_data(key, data) {
    // Ensure the key length is at least 16 bytes
    if (key.length < 16) {
        throw new Error('Key must be at least 16 bytes long');
    }

    // Use the first 16 bytes of the key for AES-128
    const keyUsed = key.slice(0, 16);
    const iv = crypto.randomBytes(16); // Generate a random IV

    // Create the cipher
    const cipher = crypto.createCipheriv('aes-128-cbc', keyUsed, iv);
    
    // Encrypt the data
    let encryptedData = cipher.update(data);
    encryptedData = Buffer.concat([encryptedData, cipher.final()]);

    // Return the encrypted data, IV, and key used for encryption
    return {
        encryptedData: encryptedData,
        iv: iv,
        keyUsed: keyUsed
    };
}
```