```c
#include <stdio.h>
#include <stdlib.h>

/**
Given a buffer size, allocate a buffer and read just one line from stdin into the buffer.

@param buf_size: the size of the buffer
@return the buffer containing the line read from stdin
*/
char* read_stdin_to_buffer(int buf_size) {
    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // graceful return on memory allocation failure
    }

    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // free allocated memory if reading fails
        return NULL; // graceful return if reading fails
    }

    return buf; // return the buffer containing the line
}
```