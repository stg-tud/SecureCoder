```cpp
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <vector>
#include <stdexcept>

std::vector<unsigned char> pad_data(const std::vector<unsigned char>& data) {
    size_t data_len = data.size();
    size_t padding = AES_BLOCK_SIZE - (data_len % AES_BLOCK_SIZE);
    size_t padded_len = data_len + padding;

    std::vector<unsigned char> padded_data(data.begin(), data.end());
    padded_data.resize(padded_len, (unsigned char)padding);

    return padded_data;
}

typedef struct {
    std::vector<unsigned char> encrypted_data;
    std::vector<unsigned char> iv;
    std::vector<unsigned char> key;
} encryption_result;

encryption_result encrypt_data(
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& data
) {
    encryption_result result;
    
    // Check if the key has sufficient length for AES (128, 192, or 256 bits)
    if (key.size() < 32) { // 256 bits
        throw std::invalid_argument("Key must be at least 32 bytes for AES-256.");
    }

    // Use the first 32 bytes of the key for AES-256
    std::vector<unsigned char> aes_key(key.begin(), key.begin() + 32);
    
    // Generate a random IV
    result.iv.resize(AES_BLOCK_SIZE);
    if (!RAND_bytes(result.iv.data(), result.iv.size())) {
        throw std::runtime_error("Failed to generate random IV.");
    }

    // Pad the data
    std::vector<unsigned char> padded_data = pad_data(data);
    result.key = aes_key; // Store the key used for encryption

    // Perform AES encryption in CBC mode
    AES_KEY encrypt_key;
    if (AES_set_encrypt_key(aes_key.data(), 256, &encrypt_key) < 0) {
        throw std::runtime_error("Failed to set AES encryption key.");
    }

    result.encrypted_data.resize(padded_data.size());
    AES_cbc_encrypt(padded_data.data(), result.encrypted_data.data(), padded_data.size(), &encrypt_key, result.iv.data(), AES_ENCRYPT);

    return result;
}
```