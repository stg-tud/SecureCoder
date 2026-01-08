#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
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

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <key_hex> <data_hex>\n", argv[0]);
        return 1;
    }

    // Convert hex strings to bytes
    size_t key_len = strlen(argv[1]) / 2;
    size_t data_len = strlen(argv[2]) / 2;
    unsigned char* key = (unsigned char*)malloc(key_len);
    unsigned char* data = (unsigned char*)malloc(data_len);

    if (!key || !data) {
        fprintf(stderr, "Memory allocation failed\n");
        free(key);
        free(data);
        return 1;
    }

    // Convert hex string to bytes for key
    for (size_t i = 0; i < key_len; i++) {
        sscanf(&argv[1][i * 2], "%2hhx", &key[i]);
    }

    // Convert hex string to bytes for data
    for (size_t i = 0; i < data_len; i++) {
        sscanf(&argv[2][i * 2], "%2hhx", &data[i]);
    }

    // Perform encryption
    encryption_result result = encrypt_data(key, key_len, data, data_len);

    if (!result.encrypted_data || !result.iv || !result.key) {
        fprintf(stderr, "Encryption failed\n");
        free(key);
        free(data);
        return 1;
    }

    // Print results in hex format
    // printf("Encrypted data: ");
    for (size_t i = 0; i < result.encrypted_len; i++) {
        printf("%02x", result.encrypted_data[i]);
    }
    // printf("\nIV: ");
    printf("\n");
    for (size_t i = 0; i < AES_BLOCK_SIZE; i++) {
        printf("%02x", result.iv[i]);
    }
    // printf("\nKey used: ");
    printf("\n");
    for (size_t i = 0; i < 16; i++) {
        printf("%02x", result.key[i]);
    }
    // printf("\n");

    // Clean up
    free(result.encrypted_data);
    free(result.iv);
    free(result.key);
    free(key);
    free(data);

    return 0;
}
