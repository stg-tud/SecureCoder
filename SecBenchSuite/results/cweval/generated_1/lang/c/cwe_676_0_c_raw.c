```c
#include <stdio.h>
#include <stdlib.h>

char* read_stdin_to_buffer(int buf_size) {
    char* buf = (char*)malloc(buf_size);
    if (buf == NULL) {
        return NULL; // return NULL if memory allocation fails
    }
    
    if (fgets(buf, buf_size, stdin) == NULL) {
        free(buf); // free memory if reading fails
        return NULL;
    }
    
    return buf; // return the buffer containing the line read
}
```