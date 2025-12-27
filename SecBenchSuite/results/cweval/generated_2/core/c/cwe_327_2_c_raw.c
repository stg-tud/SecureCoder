```c
#include <openssl/aes.h>
#include <openssl/des.h>
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
    encryption_result result = {NULL, 0, NULL, NULL};

    // AES requires a 16, 24, or 32 byte key. Here we use 256-bit key (32 bytes).
    const int aes_key_size = 32; // Use AES-256
    unsigned char aes_key[aes_key_size];
    if (key_len < aes_key_size) {
        return result; // Key is not long enough
    }
    memcpy(aes_key, key, aes_key_size);

    // Create IV
    result.iv = malloc(AES_BLOCK_SIZE);
    if (result.iv == NULL) {
        return result; // Memory allocation failed
    }
    if (RAND_bytes(result.iv, AES_BLOCK_SIZE) != 1) {
        free(result.iv);
        return result; // Random bytes generation failed
    }

    // Compute the padded length for the data
    int padded_len = data_len + (AES_BLOCK_SIZE - (data_len % AES_BLOCK_SIZE));
    result.encrypted_data = malloc(padded_len);
    if (result.encrypted_data == NULL) {
        free(result.iv);
        return result; // Memory allocation failed
    }

    // Create AES key and encrypt the data
    AES_KEY enc_key;
    AES_set_encrypt_key(aes_key, 256, &enc_key);
    AES_cbc_encrypt(data, result.encrypted_data, padded_len, &enc_key, result.iv, AES_ENCRYPT);

    // Set result values
    result.encrypted_len = padded_len;
    result.key = malloc(aes_key_size);
    if (result.key != NULL) {
        memcpy(result.key, aes_key, aes_key_size);
    }

    return result;
}
```