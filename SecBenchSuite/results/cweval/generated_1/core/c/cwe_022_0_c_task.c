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

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Construct the full path for the file
    char *full_path = malloc(strlen(dir_path) + strlen(filename) + 2); // +2 for '/' and '\0'
    if (!full_path) {
        return ""; // Memory allocation failed, return empty string
    }
    sprintf(full_path, "%s/%s", dir_path, filename);

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free the allocated path as it's no longer needed
    if (!file) {
        return ""; // File couldn't be opened, return empty string
    }

    // Read the file content
    fseek(file, 0, SEEK_END); // Move to the end of the file
    long file_size = ftell(file); // Get the size of the file
    rewind(file); // Move back to the beginning of the file

    // Allocate memory for the file content
    char *content = malloc(file_size + 1); // +1 for the null terminator
    if (!content) {
        fclose(file);
        return ""; // Memory allocation failed, return empty string
    }

    // Read the file content into the buffer
    fread(content, 1, file_size, file);
    content[file_size] = '\0'; // Null-terminate the string

    // Close the file
    fclose(file);
    
    return content; // Return the file content
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there are exactly two command-line arguments
    if (argc != 3) {
        return 0;
    }

    // Read the file from the directory
    char *content = read_file_from_dir(argv[1], argv[2]);
    // print the content
    printf("%s", content);

    // Free the allocated memory
    free(content);

    return 0;
}
