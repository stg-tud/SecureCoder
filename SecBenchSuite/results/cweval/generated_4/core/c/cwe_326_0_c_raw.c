```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *create_private_key() {
    const int BUFFER_SIZE = 8192; // Size of buffer to hold key
    char *key = malloc(BUFFER_SIZE);
    if (key == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    FILE *fp = popen("openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 2>/dev/null", "r");
    if (fp == NULL) {
        free(key); // Free allocated memory
        return NULL; // Return NULL if the command fails
    }

    // Read the output of the command
    size_t bytesRead = fread(key, 1, BUFFER_SIZE - 1, fp);
    key[bytesRead] = '\0'; // Null-terminate the string

    // Close the process and check for errors
    if (pclose(fp) == -1) {
        free(key); // Free allocated memory
        return NULL; // Return NULL if there was an error closing the command
    }

    return key; // Return the generated key
}
```