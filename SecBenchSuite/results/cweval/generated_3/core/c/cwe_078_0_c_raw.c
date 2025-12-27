```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *get_ls_result(const char *dir_path) {
    // Prepare command string
    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);

    // Create a pipe to read the command output
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return ""; // return empty string on error
    }

    // Allocate memory for the output
    char *output = malloc(4096); // Assuming max output size is 4KB
    if (output == NULL) {
        pclose(fp);
        return ""; // return empty string on memory allocation error
    }
    
    // Read the output from the command
    size_t total_length = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_length, 1, 1024, fp)) > 0) {
        total_length += bytes_read;
        // Reallocate if output buffer is filled
        if (total_length + 1024 > 4096) {
            output = realloc(output, total_length + 1024);
            if (output == NULL) {
                pclose(fp);
                return ""; // return empty string on memory allocation error
            }
        }
    }
    
    // Close the pipe
    pclose(fp);
    
    // Null-terminate the output string
    output[total_length] = '\0';
    
    // Return the output
    return output;
}
```