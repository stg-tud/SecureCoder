```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char *get_ls_result(const char *dir_path) {
    // Prepare a command to execute
    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);
    
    // Open a pipe to execute the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return "";  // Return empty string if there's an error opening the pipe
    }

    // Allocate buffer for output
    char *output = (char *)malloc(2048);  // Allocate enough space for output
    if (output == NULL) {
        pclose(fp);
        return "";  // Return empty string if memory allocation fails
    }

    // Read the command output
    size_t total_length = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output + total_length, 1, 1024, fp)) > 0) {
        total_length += bytes_read;
        if (total_length >= 2048) {
            break;  // Prevent overflow if output exceeds buffer size
        }
    }

    // Null-terminate the output string
    output[total_length] = '\0';

    // Close the pipe
    pclose(fp);

    // Return the output
    return output;
}
```