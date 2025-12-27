```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Construct the full path of the file
    char *full_path = malloc(strlen(dir_path) + strlen(filename) + 2); // +2 for '/' and '\0'
    if (full_path == NULL) {
        return NULL; // Memory allocation failed
    }
    sprintf(full_path, "%s/%s", dir_path, filename);

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free the full path after use
    if (file == NULL) {
        return strdup(""); // Return an empty string if file cannot be opened
    }

    // Move to the end of the file to determine its size
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET); // Go back to the beginning of the file

    // Allocate memory for the file content
    char *content = malloc(length + 1); // +1 for the null terminator
    if (content == NULL) {
        fclose(file);
        return NULL; // Memory allocation failed
    }

    // Read the file content
    fread(content, 1, length, file);
    content[length] = '\0'; // Null-terminate the string

    // Clean up
    fclose(file);
    return content; // Return the content of the file
}
```