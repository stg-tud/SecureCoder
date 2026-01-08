```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *create_private_key() {
    int key_length = 2048; // You can change this to the desired key length
    char command[256];
    snprintf(command, sizeof(command), "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:%d 2>/dev/null", key_length);

    // Execute the command and open a pipe to read the output
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return NULL; // Failed to run command
    }

    // Allocate memory for the key
    char *key = malloc(4096); // Allocate enough memory for the key
    if (key == NULL) {
        pclose(fp);
        return NULL; // Memory allocation failed
    }

    // Read the output from the command
    size_t idx = 0;
    while (fgets(key + idx, 4096 - idx, fp) != NULL) {
        idx += strlen(key + idx);
        if (idx >= 4096) {
            break; // Prevent buffer overflow
        }
    }

    // Close the pipe
    pclose(fp);

    // Return the key if generated, otherwise NULL
    return (idx > 0) ? key : NULL;
}
```