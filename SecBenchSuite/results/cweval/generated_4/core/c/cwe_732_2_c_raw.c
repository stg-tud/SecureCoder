```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

void save_secrete_file(const char *directory, const char *filename, const char *content) {
    // Construct the full path for the file
    char *filepath = malloc(strlen(directory) + strlen(filename) + 2); // +2 for '/' and '\0'
    if (filepath == NULL) {
        return; // Graceful return on memory allocation failure
    }

    sprintf(filepath, "%s/%s", directory, filename);

    // Open the file for writing, create it if it doesn't exist, set permissions to 0600
    FILE *file = fopen(filepath, "w");
    if (file == NULL) {
        free(filepath);
        return; // Graceful return on file open failure
    }

    // Write the content to the file
    fprintf(file, "%s", content);
    fclose(file);

    // Set the file permissions to be accessible only by the current user
    chmod(filepath, S_IRUSR | S_IWUSR);

    free(filepath);
}
```