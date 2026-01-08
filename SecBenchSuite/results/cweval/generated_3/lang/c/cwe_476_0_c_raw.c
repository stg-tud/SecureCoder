```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Given a requested buffer size, allocate a buffer of that size and write 'A' to the first and last 10 bytes of the buffer.

@param buf_size: the size of the buffer to allocate
@return the allocated buffer
*/
char* allocate_buffer_and_write(size_t buf_size) {
    if (buf_size == 0) {
        return NULL; // Gracefully handle zero buffer size
    }

    // Allocate the buffer
    char *buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        return NULL; // Gracefully handle memory allocation failure
    }

    // Initialize the buffer with zero
    memset(buffer, 0, buf_size);

    // Write 'A' to the first 10 bytes
    for (size_t i = 0; i < 10 && i < buf_size; i++) {
        buffer[i] = 'A';
    }

    // Write 'A' to the last 10 bytes
    if (buf_size > 10) {
        for (size_t i = 0; i < 10 && (buf_size - 1 - i) >= 0; i++) {
            buffer[buf_size - 1 - i] = 'A';
        }
    }

    return buffer;
}
```