```c
#include <openssl/aes.h>
#include <openssl/rand.h>
#include <string.h>
#include <stdlib.h>

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
    result.encrypted_data = NULL;
    result.iv = NULL;
    result.key = NULL;
    result.encrypted_len = 0;

    if (key_len < 32) {
        return result; // AES-256 requires a 32-byte key
    }

    // Use the first 32 bytes of the key for AES-256
    unsigned char aes_key[32];
    memcpy(aes_key, key, 32);

    // Generate a random IV
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (RAND_bytes(result.iv, AES_BLOCK_SIZE) != 1) {
        free(result.iv);
        return result; // Failed to generate random IV
    }

    // Allocate memory for the encrypted data (data_len + padding)
    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    result.encrypted_data = (unsigned char*)malloc(padded_len);
    if (!result.encrypted_data) {
        free(result.iv);
        return result; // Memory allocation failure
    }

    AES_KEY encrypt_key;
    AES_set_encrypt_key(aes_key, 256, &encrypt_key);
    
    // Perform AES encryption in CBC mode
    AES_cbc_encrypt(data, result.encrypted_data, padded_len, &encrypt_key, result.iv, AES_ENCRYPT);

    result.encrypted_len = padded_len;
    result.key = (unsigned char*)malloc(32);
    memcpy(result.key, aes_key, 32);
    
    return result;
}
```