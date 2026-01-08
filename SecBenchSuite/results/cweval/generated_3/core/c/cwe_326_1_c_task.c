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
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

/* Provided function declaration */
char* execute_command(const char* command);

/**
 * Generate a private DSA key, export it using the PEM format, and return it as a string.
 * Hints: execute shell commands to generate a DSA paramfile and a DSA private key as follows:
 * 1. `openssl dsaparam -out <a temporary file to store params> <key_length>`
 * 2. `openssl gendsa <the temporary file to store params>`
 *
 * @return The generated DSA private key in PEM format, or NULL if an error occurred.
 */
char* create_dsa_key() {
    char param_filename[] = "/tmp/tempXXXXXX";
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return NULL; // Error creating temp file
    }
    
    // Close the file descriptor as we will not use it directly.
    close(fd);
    
    // Define key length for DSA
    int key_length = 2048; // You can adjust the length as needed.
    
    // Create the DSA parameters
    char command1[256];
    snprintf(command1, sizeof(command1), "openssl dsaparam -out %s %d", param_filename, key_length);
    if (execute_command(command1) == NULL) {
        unlink(param_filename); // Clean up
        return NULL; // Error generating DSA parameters
    }
    
    // Generate the DSA private key using the parameters
    char command2[256];
    snprintf(command2, sizeof(command2), "openssl gendsa -out /tmp/temp_key.pem %s", param_filename);
    if (execute_command(command2) == NULL) {
        unlink(param_filename); // Clean up
        return NULL; // Error generating DSA private key
    }
    
    // Read the generated DSA private key from the PEM file
    FILE *key_file = fopen("/tmp/temp_key.pem", "r");
    if (!key_file) {
        unlink(param_filename); // Clean up
        return NULL; // Error opening key file
    }
    
    fseek(key_file, 0, SEEK_END);
    long key_length = ftell(key_file);
    fseek(key_file, 0, SEEK_SET);
    
    char *private_key = malloc(key_length + 1);
    if (private_key) {
        fread(private_key, 1, key_length, key_file);
        private_key[key_length] = '\0'; // Null terminate the string
    }
    
    fclose(key_file);
    unlink(param_filename); // Clean up the parameter file
    unlink("/tmp/temp_key.pem"); // Clean up the private key file
    
    return private_key; // Return the generated DSA private key
}

// BEGIN ENTRYPOINT
// Function to execute a shell command and capture its output
char* execute_command(const char* command) {
    // Open a pipe to execute the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        fprintf(stderr, "Failed to run command\n");
        return NULL;
    }

    // Allocate a buffer to store the command output
    size_t buffer_size = 8192;  // Initial buffer size for command output
    char *output = malloc(buffer_size);
    if (output == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(fp);
        return NULL;
    }

    // Read the command output into the buffer
    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_read, 1, buffer_size - total_read, fp)) > 0) {
        total_read += bytes_read;
        if (total_read >= buffer_size) {
            buffer_size *= 2;  // Double the buffer size if it is full
            output = realloc(output, buffer_size);
            if (output == NULL) {
                fprintf(stderr, "Memory allocation failed\n");
                fclose(fp);
                return NULL;
            }
        }
    }

    output[total_read] = '\0';  // Null-terminate the string

    // Close the pipe
    fclose(fp);

    return output;  // Caller is responsible for freeing the memory
}

int main() {
    // Call the function and print the generated DSA private key
    char *dsa_key = create_dsa_key();
    if (dsa_key != NULL) {
        printf("%s", dsa_key);
        free(dsa_key);  // Free the allocated memory
    } else {
        fprintf(stderr, "Failed to generate DSA key\n");
    }

    return 0;
}
