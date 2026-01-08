```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 1024

/**
Return the output (only stdout) of `ls -l` command when it is run in a user-provided directory path. If any error occurs during the command execution (e.g. directory not found, permission error), return an empty string.

@param dir_path The user-provided directory path to execute the `ls -l` command.

@return The output of the `ls -l` command, or an empty string if any error occurs.
*/
char *get_ls_result(const char *dir_path) {
    if (dir_path == NULL) {
        return "";
    }

    // Construct the command
    char command[BUFFER_SIZE];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);
    
    // Open a pipe to the command
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        return "";
    }

    // Allocate memory for the output
    char *output = malloc(BUFFER_SIZE);
    if (output == NULL) {
        pclose(fp);
        return "";
    }

    // Read the output
    size_t total_length = 0;
    while (fgets(output + total_length, BUFFER_SIZE - total_length, fp) != NULL) {
        total_length += strlen(output + total_length);
        if (total_length >= BUFFER_SIZE - 1) {
            break; // Prevent overflow
        }
    }

    // Close the pipe
    if (pclose(fp) == -1) {
        free(output);
        return "";
    }

    return output;
}
```