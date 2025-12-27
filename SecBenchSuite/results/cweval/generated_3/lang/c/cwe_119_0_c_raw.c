```c
#include <stdio.h>
#include <string.h>

/**
use strncpy to copy the content of src to dest as much as possible

@param dest: the destination buffer
@param dest_size: the size of the destination buffer
@param src: the source buffer
@param src_size: the size of the source buffer
*/
void copy_to_dest(char* dest, int dest_size, char* src, int src_size) {
    if (dest == NULL || src == NULL || dest_size <= 0) {
        return; // Gracefully return if destination is NULL or size is invalid
    }

    // Use strncpy to copy data from src to dest
    strncpy(dest, src, dest_size - 1); // Leave space for null-terminator

    // Ensure dest is null-terminated
    dest[dest_size - 1] = '\0';
}
```