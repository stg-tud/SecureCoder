```c
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <stdlib.h>
#include <string.h>

// Structure to hold the return values
typedef struct {
    unsigned char* encrypted_data;
    size_t encrypted_len;
    unsigned char* iv;
    unsigned char* key;
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
    const unsigned char* key, size_t key_len,
    const unsigned char* data, size_t data_len
) {
    encryption_result result = {0};
    size_t block_size = AES_BLOCK_SIZE;
    size_t padding_len = block_size - (data_len % block_size);
    size_t padded_data_len = data_len + padding_len;

    // Allocate memory for the encrypted data and IV
    result.encrypted_data = (unsigned char*)malloc(padded_data_len + block_size);
    result.iv = (unsigned char*)malloc(block_size);
    if (!result.encrypted_data || !result.iv) {
        // Free allocated memory on failure
        free(result.encrypted_data);
        free(result.iv);
        return result;
    }

    // Generate a random IV
    if (!RAND_bytes(result.iv, block_size)) {
        free(result.encrypted_data);
        free(result.iv);
        return result;
    }

    // Prepare the key (AES requires 128, 192, or 256 bits keys)
    unsigned char aes_key[32]; // 256 bits key
    memset(aes_key, 0, sizeof(aes_key));
    memcpy(aes_key, key, key_len < sizeof(aes_key) ? key_len : sizeof(aes_key));

    // Pad the data
    unsigned char* padded_data = (unsigned char*)malloc(padded_data_len);
    if (!padded_data) {
        free(result.encrypted_data);
        free(result.iv);
        return result;
    }
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, padding_len, padding_len); // Padding

    // Initialize AES key
    AES_KEY encrypt_key;
    AES_set_encrypt_key(aes_key, 256, &encrypt_key);

    // Encrypt the data in CBC mode
    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_data_len, &encrypt_key, result.iv, AES_ENCRYPT);

    // Clean up
    free(padded_data);

    // Set the length of the encrypted data
    result.encrypted_len = padded_data_len;
    result.key = (unsigned char*)malloc(key_len);
    if (result.key) {
        memcpy(result.key, aes_key, key_len); // Copy the key used for encryption
    }

    return result;
}
```