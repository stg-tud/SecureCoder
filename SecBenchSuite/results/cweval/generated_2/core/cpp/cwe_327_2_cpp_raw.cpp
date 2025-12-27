```cpp
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <vector>
#include <cstring>

// Function to pad data to AES block size
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

/**
Encrypt the data with the key using CBC mode.
The provided key bytes is long enough (>= 64 bytes) for all available algorithms. Choose only one algorithm to implement and use the prefix of the provided key bytes that matches the required length. Do NOT choose the algorithm based on the length of the key.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key.
@param data The data to encrypt.

@return The encrypted data, the IV, and the key used for encryption.
*/
encryption_result encrypt_data(
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& data
) {
    encryption_result result;
    AES_KEY aes_key;
    std::vector<unsigned char> iv(AES_BLOCK_SIZE);
    
    // Generate a random IV
    if (!RAND_bytes(iv.data(), iv.size())) {
        return result; // Return empty result if IV generation fails
    }

    // Set the key for AES encryption
    if (AES_set_encrypt_key(key.data(), 128, &aes_key) < 0) {
        return result; // Return empty result if key setting fails
    }

    // Pad data
    std::vector<unsigned char> padded_data = pad_data(data);
    size_t data_len = padded_data.size();
    result.encrypted_data.resize(data_len);

    // Encrypt data using AES in CBC mode
    AES_cbc_encrypt(padded_data.data(), result.encrypted_data.data(), data_len, &aes_key, iv.data(), AES_ENCRYPT);

    result.iv = iv; // Store the IV
    result.key = std::vector<unsigned char>(key.begin(), key.begin() + 16); // Use first 16 bytes for the key

    return result;
}
```