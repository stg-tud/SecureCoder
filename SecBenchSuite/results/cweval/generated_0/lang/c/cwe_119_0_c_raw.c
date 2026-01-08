```c
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
        return; // Gracefully return if the input is invalid
    }

    // Use strncpy to copy from src to dest, ensuring we do not exceed dest_size
    strncpy(dest, src, dest_size - 1);

    // Null-terminate the destination buffer
    dest[dest_size - 1] = '\0';
}
```