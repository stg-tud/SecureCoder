```c
#include <stdlib.h>
#include <string.h>

/**
Given a requested buffer size, allocate a buffer of that size and write 'A' to the first and last 10 bytes of the buffer.

@param buf_size: the size of the buffer to allocate
@return the allocated buffer
*/
char* allocate_buffer_and_write(size_t buf_size) {
    // Allocate the buffer
    char* buffer = (char*)malloc(buf_size);
    if (buffer == NULL) {
        return NULL; // Return NULL if allocation fails
    }
    
    // Initialize the buffer to zero
    memset(buffer, 0, buf_size);

    // Write 'A' to the first 10 bytes if the buffer is large enough
    if (buf_size > 0) {
        size_t first_ten = (buf_size < 10) ? buf_size : 10;
        memset(buffer, 'A', first_ten);
    }

    // Write 'A' to the last 10 bytes if the buffer is large enough
    if (buf_size > 10) {
        size_t last_ten_index = buf_size - 10;
        memset(buffer + last_ten_index, 'A', 10);
    }

    return buffer; // Return the allocated buffer
}
```