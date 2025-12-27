```c
#include <stdio.h>
#include <stdlib.h>

char* read_stdin_to_buffer(int buf_size) {
    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Gracefully return if allocation fails
    }
    
    // Use fgets to read a line from stdin into the buffer
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // Free allocated memory if reading fails
        return NULL; // Gracefully return if reading fails
    }
    
    return buf; // Return the buffer containing the line read
}
```