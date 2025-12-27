```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char* write_results(const char* results) {
    // Create a temporary file
    char* temp_filename = tmpnam(NULL);
    if (temp_filename == NULL) {
        return NULL; // Return NULL if tmpnam fails
    }

    // Open the temporary file for writing
    FILE* temp_file = fopen(temp_filename, "w");
    if (temp_file == NULL) {
        return NULL; // Return NULL if fopen fails
    }

    // Write the results to the temporary file
    if (fprintf(temp_file, "%s", results) < 0) {
        fclose(temp_file);
        return NULL; // Return NULL if writing fails
    }

    // Close the temporary file
    fclose(temp_file);

    // Return the dynamically allocated string containing the temporary file name
    char* result_filename = malloc(strlen(temp_filename) + 1);
    if (result_filename == NULL) {
        return NULL; // Return NULL if malloc fails
    }
    
    strcpy(result_filename, temp_filename);
    return result_filename;
}
```