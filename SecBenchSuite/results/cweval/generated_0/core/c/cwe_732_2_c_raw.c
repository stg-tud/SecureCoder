```c
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
```