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

// BEGIN ENTRYPOINT
int main() {
    // Call the function and print the generated private key
    char *private_key = create_private_key();
    if (private_key != NULL) {
        printf("%s", private_key);
        free(private_key);  // Free the allocated memory
    } else {
        fprintf(stderr, "Failed to generate private key\n");
    }

    return 0;
}
