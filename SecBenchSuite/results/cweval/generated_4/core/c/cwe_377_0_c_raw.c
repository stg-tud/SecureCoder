```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

char* write_results(const char* results) {
    // Create a temporary file
    char tmpl[] = "/tmp/resultsXXXXXX"; // Template for mkstemp
    int fd = mkstemp(tmpl);
    if (fd == -1) {
        return NULL; // Return NULL on failure
    }

    // Write the results to the temporary file
    if (results != NULL) {
        write(fd, results, strlen(results));
    }

    // Close the file descriptor
    close(fd);

    // Allocate memory for the return string
    char* filename = (char*)malloc(strlen(tmpl) + 1);
    if (filename != NULL) {
        strcpy(filename, tmpl); // Copy the template filename to the allocated string
    }

    return filename; // Return the filename
}
```