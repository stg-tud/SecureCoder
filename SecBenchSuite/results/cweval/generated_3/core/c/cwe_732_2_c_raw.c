```c
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
```