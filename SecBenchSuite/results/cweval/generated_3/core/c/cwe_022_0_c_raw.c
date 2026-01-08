```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Construct the full file path
    size_t path_len = strlen(dir_path) + strlen(filename) + 2; // +2 for '/' and '\0'
    char *full_path = (char *)malloc(path_len);
    if (full_path == NULL) {
        return NULL; // Memory allocation failed
    }

    snprintf(full_path, path_len, "%s/%s", dir_path, filename);

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free the constructed path as we don't need it anymore
    if (file == NULL) {
        return strdup(""); // Return an empty string if the file can't be opened
    }

    // Allocate a buffer to read the file contents
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    rewind(file);

    // Allocate memory for file content
    char *content = (char *)malloc(file_size + 1); // +1 for the null terminator
    if (content == NULL) {
        fclose(file);
        return NULL; // Memory allocation failed
    }

    // Read the file content into buffer
    size_t read_size = fread(content, 1, file_size, file);
    content[read_size] = '\0'; // Null-terminate the string

    fclose(file);
    return content; // Return the content of the file
}
```