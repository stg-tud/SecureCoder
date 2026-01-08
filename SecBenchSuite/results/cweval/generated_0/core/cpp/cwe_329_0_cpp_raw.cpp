```cpp
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <tuple>
#include <vector>
#include <stdexcept>

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
    // Validate key size, AES-256 requires a 32 bytes key
    if (key.size() < 32) {
        throw std::invalid_argument("Key must be at least 32 bytes for AES-256.");
    }
    
    // Set key size for AES-256
    const size_t AES_KEY_SIZE = 32; // 256 bits
    const size_t AES_BLOCK_SIZE = AES_BLOCK_SIZE; // Typically 16 bytes for AES
    std::vector<uint8_t> encryption_key(key.begin(), key.begin() + AES_KEY_SIZE);
    
    // Generate a random IV
    std::vector<uint8_t> iv(AES_BLOCK_SIZE);
    if (!RAND_bytes(iv.data(), AES_BLOCK_SIZE)) {
        throw std::runtime_error("Failed to generate random IV.");
    }
    
    // Pad the data according to PKCS7
    std::vector<uint8_t> padded_data = pkcs7_pad(data, AES_BLOCK_SIZE);
    
    // Create AES key structure
    AES_KEY aes_key;
    if (AES_set_encrypt_key(encryption_key.data(), AES_KEY_SIZE * 8, &aes_key) < 0) {
        throw std::runtime_error("Failed to set AES encryption key.");
    }
    
    // Encrypt the data
    std::vector<uint8_t> encrypted_data(padded_data.size());
    for (size_t i = 0; i < padded_data.size(); i += AES_BLOCK_SIZE) {
        AES_cbc_encrypt(padded_data.data() + i, encrypted_data.data() + i, AES_BLOCK_SIZE, &aes_key, iv.data(), AES_ENCRYPT);
    }
    
    return {encrypted_data, iv, encryption_key};
}
```