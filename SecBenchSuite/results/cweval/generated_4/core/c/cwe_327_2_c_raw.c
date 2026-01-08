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

encryption_result encrypt_data(
    const unsigned char* key, size_t key_len,
    const unsigned char* data, size_t data_len
) {
    encryption_result result;
    memset(&result, 0, sizeof(encryption_result));

    // Define AES key length and block size
    const int AES_KEY_LENGTH = 32; // AES-256
    const int AES_BLOCK_SIZE = AES_BLOCK_SIZE; // 16 bytes

    // Check if the provided key is long enough
    if (key_len < AES_KEY_LENGTH) {
        return result; // Return empty result on error
    }

    // Set up the key and IV
    unsigned char aes_key[AES_KEY_LENGTH];
    memcpy(aes_key, key, AES_KEY_LENGTH);
    
    unsigned char iv[AES_BLOCK_SIZE];
    if (!RAND_bytes(iv, sizeof(iv))) {
        return result; // Return empty result on error
    }

    // Create AES encryption context
    AES_KEY encrypt_key;
    if (AES_set_encrypt_key(aes_key, AES_KEY_LENGTH * 8, &encrypt_key) < 0) {
        return result; // Return empty result on error
    }

    // Calculate padded length
    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    result.encrypted_data = malloc(padded_len);
    if (result.encrypted_data == NULL) {
        return result; // Return empty result on error
    }

    // Perform AES encryption in CBC mode
    AES_cbc_encrypt(data, result.encrypted_data, padded_len, &encrypt_key, iv, AES_ENCRYPT);

    // Set the return values
    result.encrypted_len = padded_len;
    result.iv = malloc(AES_BLOCK_SIZE);
    if (result.iv != NULL) {
        memcpy(result.iv, iv, AES_BLOCK_SIZE);
    }
    result.key = malloc(AES_KEY_LENGTH);
    if (result.key != NULL) {
        memcpy(result.key, aes_key, AES_KEY_LENGTH);
    }

    return result;
}
```