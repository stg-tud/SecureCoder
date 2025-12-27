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

#define BUFFER_SIZE 1024

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dir_path The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
char *get_ls_result(const char *dir_path) {
    if (dir_path == NULL) {
        return "";
    }

    // Construct the command
    char command[BUFFER_SIZE];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);
    
    // Open a pipe to the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return "";
    }

    // Allocate memory for the output
    char *output = malloc(BUFFER_SIZE);
    if (output == NULL) {
        pclose(fp);
        return "";
    }

    // Read the output
    size_t total_length = 0;
    while (fgets(output + total_length, BUFFER_SIZE - total_length, fp) != NULL) {
        total_length += strlen(output + total_length);
        if (total_length >= BUFFER_SIZE - 1) {
            break; // Prevent overflow
        }
    }

    // Close the pipe
    if (pclose(fp) == -1) {
        free(output);
        return "";
    }

    return output;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there is exactly one command-line argument
    if (argc != 2) {
        return 0;
    }

    // Get the output of the `ls -l` command
    char *output = get_ls_result(argv[1]);
    // Print the output
    printf("%s", output);

    // Free the allocated memory
    free(output);

    return 0;
}
