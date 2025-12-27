```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *create_private_key() {
    const int key_length = 2048; // You can adjust the key length as needed
    char command[256];
    snprintf(command, sizeof(command), "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d 2>/dev/null", key_length);
    
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return NULL; // Error executing command
    }

    // Initialize buffer to hold the key
    size_t buffer_size = 4096; // Adjust size if needed
    char *private_key = malloc(buffer_size);
    if (private_key == NULL) {
        pclose(fp);
        return NULL; // Memory allocation failed
    }

    // Read the output from the command
    size_t bytes_read = fread(private_key, 1, buffer_size - 1, fp);
    private_key[bytes_read] = '\0'; // Null-terminate the string

    pclose(fp);

    // If no data was read, return NULL
    if (bytes_read == 0) {
        free(private_key);
        return NULL; // No key generated
    }

    return private_key;
}
```