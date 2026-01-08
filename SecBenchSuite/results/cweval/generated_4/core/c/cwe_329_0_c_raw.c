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
Encrypt the data with the key using AES and CBC mode.
The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

@param key The bytes to generate the encryption key.
@param data The data to encrypt.

@return The encrypted data, the IV, and the key used for encryption.
*/
encryption_result encrypt_data(
    const unsigned char* key, size_t key_len,
    const unsigned char* data, size_t data_len
) {
    encryption_result result;
    AES_KEY aes_key;
    unsigned char iv[AES_BLOCK_SIZE];
    size_t block_count, padded_len;

    // Initialize the result variables
    result.encrypted_data = NULL;
    result.iv = NULL;
    result.key = NULL;

    // Generate a random IV
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        return result; // Return gracefully on failure
    }

    // Set the key length to 256 bits (32 bytes)
    size_t aes_key_len = 32; // 256 bits
    if (key_len < aes_key_len) {
        return result; // Return gracefully if key is too short
    }

    // Set the encryption key
    if (AES_set_encrypt_key(key, 256, &aes_key) < 0) {
        return result; // Return gracefully on failure
    }

    // Calculate the number of blocks needed for padding
    block_count = (data_len + AES_BLOCK_SIZE - 1) / AES_BLOCK_SIZE;
    padded_len = block_count * AES_BLOCK_SIZE;

    // Allocate memory for the encrypted data
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (!result.encrypted_data) {
        return result; // Return gracefully on memory allocation failure
    }

    // Allocate memory for the key copy
    result.key = (unsigned char*)malloc(aes_key_len);
    if (!result.key) {
        free(result.encrypted_data);
        result.encrypted_data = NULL;
        return result; // Return gracefully on memory allocation failure
    }
    
    // Copy the relevant portion of the key
    memcpy(result.key, key, aes_key_len);

    // Perform the encryption
    AES_cbc_encrypt(data, result.encrypted_data, padded_len, &aes_key, iv, AES_ENCRYPT);

    // Set the result fields
    result.encrypted_len = padded_len;
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (result.iv) {
        memcpy(result.iv, iv, AES_BLOCK_SIZE);
    }

    return result;
}
```