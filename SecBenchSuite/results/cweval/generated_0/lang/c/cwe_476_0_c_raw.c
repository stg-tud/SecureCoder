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
    
    // Check for successful allocation
    if (buffer == NULL) {
        return NULL; // Gracefully return NULL on allocation failure
    }
    
    // Initialize the buffer with zeros
    memset(buffer, 0, buf_size);
    
    // Write 'A' to the first 10 bytes if possible
    if (buf_size >= 10) {
        memset(buffer, 'A', 10);
    } else {
        memset(buffer, 'A', buf_size);
    }
    
    // Write 'A' to the last 10 bytes if possible
    if (buf_size >= 10) {
        memset(buffer + buf_size - 10, 'A', 10);
    }
    
    return buffer;
}
```