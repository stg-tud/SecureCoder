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
    memset(&result, 0, sizeof(encryption_result));

    // AES key length (256 bits = 32 bytes)
    const size_t aes_key_len = 32;
    unsigned char aes_key[aes_key_len];
    
    // Use the first 32 bytes of the provided key
    if (key_len < aes_key_len) {
        return result; // Return empty result if key is too short
    }
    memcpy(aes_key, key, aes_key_len);

    // Create IV
    result.iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    if (result.iv == NULL) {
        return result; // Return empty result if allocation fails
    }
    if (RAND_bytes(result.iv, AES_BLOCK_SIZE) != 1) {
        free(result.iv);
        return result; // Return empty result if random bytes generation fails
    }

    // Padding the data to be a multiple of AES_BLOCK_SIZE
    size_t padding_len = AES_BLOCK_SIZE - (data_len % AES_BLOCK_SIZE);
    size_t padded_data_len = data_len + padding_len;
    unsigned char* padded_data = (unsigned char*)malloc(padded_data_len);
    if (padded_data == NULL) {
        free(result.iv);
        return result; // Return empty result if allocation fails
    }
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, padding_len, padding_len);

    // Allocate memory for encrypted data
    result.encrypted_data = (unsigned char*)malloc(padded_data_len);
    if (result.encrypted_data == NULL) {
        free(padded_data);
        free(result.iv);
        return result; // Return empty result if allocation fails
    }

    // Set up AES CBC encryption
    AES_KEY encryptKey;
    if (AES_set_encrypt_key(aes_key, 256, &encryptKey) < 0) {
        free(padded_data);
        free(result.encrypted_data);
        free(result.iv);
        return result; // Return empty result if key setup fails
    }

    // Perform AES encryption
    AES_cbc_encrypt(padded_data, result.encrypted_data, padded_data_len, &encryptKey, result.iv, AES_ENCRYPT);

    // Set the lengths in the result struct
    result.encrypted_len = padded_data_len;
    result.key = (unsigned char*)malloc(aes_key_len);
    if (result.key != NULL) {
        memcpy(result.key, aes_key, aes_key_len);
    }

    // Clean up
    free(padded_data);
    return result;
}
```