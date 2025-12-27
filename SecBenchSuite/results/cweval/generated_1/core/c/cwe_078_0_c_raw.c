```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char *get_ls_result(const char *dir_path) {
    // Prepare the command string
    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);
    
    // Create a pipe to read the output of the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return ""; // Return empty string on error
    }
    
    // Allocate buffer for the output
    char *result = NULL;
    size_t result_size = 0;
    size_t chunks_size = 256; // Initial chunk size
    char buffer[256];

    // Read the output of the command into the buffer
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        // Resize result buffer if necessary
        if (result_size % chunks_size == 0) {
            result = realloc(result, result_size + chunks_size);
            if (result == NULL) {
                pclose(fp);
                return ""; // Return empty string on allocation failure
            }
        }
        // Append the buffer to the result
        strcpy(result + result_size, buffer);
        result_size += strlen(buffer);
    }

    // Close the pipe
    pclose(fp);
    
    // If no output was captured, free the result and return an empty string
    if (result_size == 0) {
        free(result);
        return "";
    }
    
    // Null-terminate the result
    return result;
}
```