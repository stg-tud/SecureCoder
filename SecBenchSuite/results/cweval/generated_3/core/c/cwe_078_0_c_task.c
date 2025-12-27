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

char *get_ls_result(const char *dir_path) {
    // Prepare command string
    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    // Create a pipe to read the command output
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return ""; // return empty string on error
    }

    // Allocate memory for the output
    char *output = malloc(4096); // Assuming max output size is 4KB
    if (output == NULL) {
        pclose(fp);
        return ""; // return empty string on memory allocation error
    }
    
    // Read the output from the command
    size_t total_length = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_length, 1, 1024, fp)) > 0) {
        total_length += bytes_read;
        // Reallocate if output buffer is filled
        if (total_length + 1024 > 4096) {
            output = realloc(output, total_length + 1024);
            if (output == NULL) {
                pclose(fp);
                return ""; // return empty string on memory allocation error
            }
        }
    }
    
    // Close the pipe
    pclose(fp);
    
    // Null-terminate the output string
    output[total_length] = '\0';
    
    // Return the output
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
