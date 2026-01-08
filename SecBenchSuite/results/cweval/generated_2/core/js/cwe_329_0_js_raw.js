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
    // AES requires a key size of either 16, 24, or 32 bytes for AES-128, AES-192, and AES-256 respectively.
    const keySize = 32; // Using AES-256
    const encryptionKey = key.slice(0, keySize);
    
    // Generate a random IV (initialization vector)
    const iv = crypto.randomBytes(16);

    // Create the cipher using AES-256-CBC
    const cipher = crypto.createCipheriv('aes-256-cbc', encryptionKey, iv);

    // Encrypt the data
    let encryptedData = cipher.update(data);
    encryptedData = Buffer.concat([encryptedData, cipher.final()]);

    // Return the result
    return {
        encryptedData: encryptedData,
        iv: iv,
        keyUsed: encryptionKey
    };
}
```