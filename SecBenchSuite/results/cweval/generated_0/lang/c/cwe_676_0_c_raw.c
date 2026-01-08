```c
#include <stdio.h>
#include <stdlib.h>

char* read_stdin_to_buffer(int buf_size) {
    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // Return NULL if allocation fails
    }
    
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // Free the buffer if reading fails
        return NULL; // Return NULL if reading fails
    }
    
    return buf; // Return the buffer containing the line read
}
```