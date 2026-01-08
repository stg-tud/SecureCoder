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
