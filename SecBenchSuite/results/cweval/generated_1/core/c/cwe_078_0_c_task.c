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

char *get_ls_result(const char *dir_path) {
    // Prepare the command string
    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);
    
    // Create a pipe to read the output of the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return ""; // Return empty string on error
    }
    
    // Allocate buffer for the output
    char *result = NULL;
    size_t result_size = 0;
    size_t chunks_size = 256; // Initial chunk size
    char buffer[256];

    // Read the output of the command into the buffer
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        // Resize result buffer if necessary
        if (result_size % chunks_size == 0) {
            result = realloc(result, result_size + chunks_size);
            if (result == NULL) {
                pclose(fp);
                return ""; // Return empty string on allocation failure
            }
        }
        // Append the buffer to the result
        strcpy(result + result_size, buffer);
        result_size += strlen(buffer);
    }

    // Close the pipe
    pclose(fp);
    
    // If no output was captured, free the result and return an empty string
    if (result_size == 0) {
        free(result);
        return "";
    }
    
    // Null-terminate the result
    return result;
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
