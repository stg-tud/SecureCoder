```c
#include <openssl/aes.h>
#include <openssl/des.h>
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
    encryption_result result;
    AES_KEY enc_key;
    unsigned char* iv = (unsigned char*)malloc(AES_BLOCK_SIZE);
    size_t padded_len = ((data_len + AES_BLOCK_SIZE) / AES_BLOCK_SIZE) * AES_BLOCK_SIZE; // Padding length
    unsigned char* padded_data = (unsigned char*)malloc(padded_len);
    unsigned char* encrypted_data = (unsigned char*)malloc(padded_len);
    
    if (!iv || !padded_data || !encrypted_data) {
        result.encrypted_data = NULL;
        result.encrypted_len = 0;
        result.iv = NULL;
        result.key = NULL;
        return result; // Memory allocation failed
    }

    // Generate a random IV
    if (RAND_bytes(iv, AES_BLOCK_SIZE) != 1) {
        free(iv);
        free(padded_data);
        free(encrypted_data);
        result.encrypted_data = NULL;
        result.encrypted_len = 0;
        result.iv = NULL;
        result.key = NULL;
        return result; // IV generation failed
    }

    // Padding the input data
    memcpy(padded_data, data, data_len);
    memset(padded_data + data_len, 0, padded_len - data_len); // Zero padding

    // Set the encryption key
    if (AES_set_encrypt_key(key, 128, &enc_key) != 0) {
        free(iv);
        free(padded_data);
        free(encrypted_data);
        result.encrypted_data = NULL;
        result.encrypted_len = 0;
        result.iv = NULL;
        result.key = NULL;
        return result; // Key setup failed
    }

    // Encrypt data in CBC mode
    AES_cbc_encrypt(padded_data, encrypted_data, padded_len, &enc_key, iv, AES_ENCRYPT);

    // Populate the result structure
    result.encrypted_data = encrypted_data;
    result.encrypted_len = padded_len;
    result.iv = iv;
    result.key = (unsigned char*)malloc(16); // AES-128 uses a 16-byte key
    memcpy(result.key, key, 16); // Copy the first 16 bytes of the key

    // Free intermediate buffers
    free(padded_data);
    
    return result; // Return the result
}
```