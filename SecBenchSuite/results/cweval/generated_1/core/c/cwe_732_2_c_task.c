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
    // Construct the full path for the file
    char *filepath = malloc(strlen(directory) + strlen(filename) + 2); // +2 for '/' and '\0'
    if (!filepath) {
        return; // Handle memory allocation failure
    }
    sprintf(filepath, "%s/%s", directory, filename);

    // Create and open the file for writing
    FILE *file = fopen(filepath, "w");
    if (!file) {
        free(filepath);
        return; // Handle file opening failure
    }

    // Write the content to the file
    fprintf(file, "%s", content);
    fclose(file);

    // Change the file permissions to be accessible only by the current user
    // This corresponds to 0600 in octal (read/write for user only)
    chmod(filepath, S_IRUSR | S_IWUSR);

    // Clean up
    free(filepath);
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
