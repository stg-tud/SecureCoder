```c
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
```