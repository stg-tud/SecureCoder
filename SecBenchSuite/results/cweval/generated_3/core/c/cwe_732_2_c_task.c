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
#include <sys/stat.h>
#include <unistd.h>

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    if (directory == NULL || filename == NULL || content == NULL) {
        return; // Gracefully return if any parameter is NULL
    }

    // Create the full path for the secret file
    char *full_path = malloc(strlen(directory) + strlen(filename) + 2); // +2 for '/' and '\0'
    if (full_path == NULL) {
        return; // Gracefully return if memory allocation fails
    }
    sprintf(full_path, "%s/%s", directory, filename);

    // Open the file for writing
    FILE *file = fopen(full_path, "w");
    if (file == NULL) {
        free(full_path);
        return; // Gracefully return if file opening fails
    }

    // Write the content to the file
    fputs(content, file);

    // Close the file
    fclose(file);

    // Change file permissions to be accessible only by the user
    mode_t mode = S_IRUSR | S_IWUSR; // Read and write permissions for the owner only
    if (chmod(full_path, mode) != 0) {
        // If chmod fails, we gracefully return but don't handle this case further
    }

    // Free the allocated memory
    free(full_path);
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there are exactly four command-line arguments
    if (argc != 4) {
        return 0;
    }

    // Save the secret file
    save_secrete_file(argv[1], argv[2], argv[3]);

    return 0;
}
