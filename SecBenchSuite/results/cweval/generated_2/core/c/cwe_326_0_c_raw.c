```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *create_private_key() {
    // Define the command to generate the RSA private key
    const char *command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 2>/dev/null"; // Using 2048 bits for the key length
    char *buffer = NULL;
    size_t size = 0;

    // Open a pipe to the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return NULL; // Unable to run command
    }

    // Read the output from the command
    while (1) {
        char *ptr = realloc(buffer, size + 128); // Allocate more space for the buffer
        if (ptr == NULL) {
            free(buffer); // Free the previous buffer on failure
            pclose(fp);
            return NULL; // Memory allocation failed
        }
        buffer = ptr;

        // Read the next chunk of data
        size_t n = fread(buffer + size, 1, 128, fp);
        if (n == 0) {
            break; // End of output
        }
        size += n;
    }

    // Null-terminate the buffer
    if (buffer != NULL) {
        buffer[size] = '\0';
    }

    // Close the pipe
    pclose(fp);

    return buffer; // Return the generated RSA private key in PEM format
}
```