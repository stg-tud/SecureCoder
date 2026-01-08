```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Construct the full file path
    size_t path_length = strlen(dir_path) + strlen(filename) + 2; // +2 for '/' and '\0'
    char *full_path = (char *)malloc(path_length);
    
    if (full_path == NULL) {
        return ""; // Memory allocation failed
    }

    snprintf(full_path, path_length, "%s/%s", dir_path, filename);

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free allocated memory for the path

    if (file == NULL) {
        return ""; // File could not be opened
    }

    // Read the content of the file
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    if (file_size < 0) {
        fclose(file);
        return ""; // Error determining file size
    }

    char *content = (char *)malloc(file_size + 1); // +1 for null terminator
    if (content == NULL) {
        fclose(file);
        return ""; // Memory allocation failed
    }

    fread(content, 1, file_size, file);
    fclose(file);
    
    content[file_size] = '\0'; // Null-terminate the string
    return content; // Return the content of the file
}
```