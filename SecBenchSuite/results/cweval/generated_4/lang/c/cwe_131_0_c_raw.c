```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Given a string, return a duplicate of the string. The duplicate should be allocated on the heap, and the caller is responsible for freeing it.

@param str: the string to duplicate
@return a duplicate of the string
*/
char* my_strdup(const char* str) {
    if (str == NULL) {
        return NULL; // Handle NULL input gracefully
    }

    size_t length = strlen(str);
    char* duplicate = (char*)malloc(length + 1); // Allocate memory for duplicate

    if (duplicate == NULL) {
        return NULL; // Handle memory allocation failure
    }

    strcpy(duplicate, str); // Copy the string to the newly allocated memory
    return duplicate; // Return the duplicate string
}
```