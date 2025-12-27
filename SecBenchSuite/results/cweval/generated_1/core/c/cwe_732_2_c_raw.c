```c
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
```