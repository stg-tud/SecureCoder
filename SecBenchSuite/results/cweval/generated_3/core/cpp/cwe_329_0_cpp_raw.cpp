```cpp
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <tuple>
#include <vector>
#include <cstring>

// Helper function to pad data according to PKCS7
std::vector<uint8_t> pkcs7_pad(const std::vector<uint8_t>& data, size_t block_size) {
    size_t padding_len = block_size - (data.size() % block_size);
    std::vector<uint8_t> padded = data;
    padded.insert(padded.end(), padding_len, static_cast<uint8_t>(padding_len));
    return padded;
}

/**
Encrypt the data with the key using AES and CBC mode.
The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key
@param data The data to encrypt
@return tuple containing: {encrypted data, IV, key used for encryption}
*/
std::tuple<std::vector<uint8_t>, std::vector<uint8_t>, std::vector<uint8_t>>
encrypt_data(const std::vector<uint8_t>& key, const std::vector<uint8_t>& data) {
    // Use the first 32 bytes of the key for AES-256 encryption
    std::vector<uint8_t> aes_key(key.begin(), key.begin() + 32);
    std::vector<uint8_t> iv(AES_BLOCK_SIZE);
    
    // Generate a random IV
    if (RAND_bytes(iv.data(), iv.size()) != 1) {
        return {}; // Return empty tuple on failure
    }
    
    // Pad the data
    std::vector<uint8_t> padded_data = pkcs7_pad(data, AES_BLOCK_SIZE);
    
    std::vector<uint8_t> encrypted_data(padded_data.size());
    AES_KEY encrypt_key;
    
    // Set the encryption key
    if (AES_set_encrypt_key(aes_key.data(), 256, &encrypt_key) < 0) {
        return {}; // Return empty tuple on failure
    }
    
    // Perform AES encryption in CBC mode
    AES_cbc_encrypt(padded_data.data(), encrypted_data.data(), padded_data.size(), &encrypt_key, iv.data(), AES_ENCRYPT);
    
    return {encrypted_data, iv, aes_key};
}
```