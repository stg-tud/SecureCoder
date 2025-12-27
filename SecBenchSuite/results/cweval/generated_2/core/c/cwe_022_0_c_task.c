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
    // Construct the full file path
    size_t path_length = strlen(dir_path) + strlen(filename) + 2; // +2 for '/' and '\0'
    char *full_path = (char *)malloc(path_length);
    
    if (full_path == NULL) {
        return ""; // Memory allocation failed
    }

    snprintf(full_path, path_length, "%s/%s", dir_path, filename);

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free allocated memory for the path

    if (file == NULL) {
        return ""; // File could not be opened
    }

    // Read the content of the file
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    if (file_size < 0) {
        fclose(file);
        return ""; // Error determining file size
    }

    char *content = (char *)malloc(file_size + 1); // +1 for null terminator
    if (content == NULL) {
        fclose(file);
        return ""; // Memory allocation failed
    }

    fread(content, 1, file_size, file);
    fclose(file);
    
    content[file_size] = '\0'; // Null-terminate the string
    return content; // Return the content of the file
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
