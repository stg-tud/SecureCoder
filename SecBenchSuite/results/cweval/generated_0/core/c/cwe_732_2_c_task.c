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
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    // Create the full path for the secret file
    char filepath[1024];
    snprintf(filepath, sizeof(filepath), "%s/%s", directory, filename);
    
    // Open the file for writing
    FILE *file = fopen(filepath, "w");
    if (file == NULL) {
        perror("Failed to open file for writing");
        return;
    }

    // Write the content to the file
    if (fwrite(content, sizeof(char), strlen(content), file) < strlen(content)) {
        perror("Failed to write content to file");
        fclose(file);
        return;
    }

    // Close the file
    fclose(file);

    // Change the file permissions to be accessible only by the current user
    struct stat st;
    if (stat(filepath, &st) == 0) {
        // Set the file owner to the current user and set permissions to 600 (rw-------)
        if (chown(filepath, getuid(), -1) < 0) {
            perror("Failed to change file owner");
        }
        if (chmod(filepath, S_IRUSR | S_IWUSR) < 0) {
            perror("Failed to change file permissions");
        }
    } else {
        perror("Failed to get file status");
    }
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
