```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *read_file_from_dir(const char *filename, const char *dir_path) {
    // Construct the full path for the file
    char *full_path = malloc(strlen(dir_path) + strlen(filename) + 2); // +2 for '/' and '\0'
    if (!full_path) {
        return ""; // Memory allocation failed, return empty string
    }
    sprintf(full_path, "%s/%s", dir_path, filename);

    // Open the file for reading
    FILE *file = fopen(full_path, "r");
    free(full_path); // Free the allocated path as it's no longer needed
    if (!file) {
        return ""; // File couldn't be opened, return empty string
    }

    // Read the file content
    fseek(file, 0, SEEK_END); // Move to the end of the file
    long file_size = ftell(file); // Get the size of the file
    rewind(file); // Move back to the beginning of the file

    // Allocate memory for the file content
    char *content = malloc(file_size + 1); // +1 for the null terminator
    if (!content) {
        fclose(file);
        return ""; // Memory allocation failed, return empty string
    }

    // Read the file content into the buffer
    fread(content, 1, file_size, file);
    content[file_size] = '\0'; // Null-terminate the string

    // Close the file
    fclose(file);
    
    return content; // Return the file content
}
```