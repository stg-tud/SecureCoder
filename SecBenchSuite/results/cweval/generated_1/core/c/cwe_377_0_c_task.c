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

char* write_results(const char* results) {
    // Create a temporary file
    char* temp_filename = tmpnam(NULL);
    if (temp_filename == NULL) {
        return NULL; // return NULL if unable to create a temp filename
    }

    // Open the temporary file for writing
    FILE* temp_file = fopen(temp_filename, "w");
    if (temp_file == NULL) {
        return NULL; // return NULL if unable to open the file
    }

    // Write the results to the temporary file
    if (fputs(results, temp_file) == EOF) {
        fclose(temp_file);
        return NULL; // return NULL if unable to write to the file
    }

    // Close the temporary file
    fclose(temp_file);

    // Return a dynamically allocated string containing the temporary file name
    char* result_filename = malloc(strlen(temp_filename) + 1);
    if (result_filename == NULL) {
        return NULL; // return NULL if unable to allocate memory
    }
    strcpy(result_filename, temp_filename);
    
    return result_filename; // Return the filename
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <string_to_write>\n", argv[0]);
        return 1;
    }

    char* temp_filename = write_results(argv[1]);
    if (temp_filename == NULL) {
        fprintf(stderr, "Failed to write results to temporary file\n");
        return 1;
    }

    printf("%s", temp_filename);

    // Clean up
    free(temp_filename);

    return 0;
}
