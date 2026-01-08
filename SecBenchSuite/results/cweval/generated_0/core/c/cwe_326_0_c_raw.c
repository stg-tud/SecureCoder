```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *create_private_key() {
    const char *command_template = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 2>/dev/null";
    FILE *fp;
    char *buffer = NULL;
    size_t size = 0;
    size_t read_size = 0;

    /* Open the command for reading. */
    fp = popen(command_template, "r");
    if (fp == NULL) {
        return NULL; // Error occurred when opening the command
    }

    /* Allocate an initial buffer for the output */
    buffer = malloc(4096); // Allocate space for the key
    if (buffer == NULL) {
        pclose(fp);
        return NULL; // Memory allocation error
    }

    /* Read the output a line at a time - output it. */
    read_size = fread(buffer, sizeof(char), 4096, fp);
    if (read_size > 0) {
        buffer[read_size] = '\0'; // Null-terminate the string
    } else {
        free(buffer);
        buffer = NULL; // No output read
    }

    /* Close the command */
    if (pclose(fp) == -1) {
        free(buffer);
        return NULL; // Error occurred when closing the command
    }

    return buffer; // Return the generated RSA private key in PEM format
}
```