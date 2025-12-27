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
        return NULL; // Handle null input
    }

    size_t len = strlen(str); // Get the length of the original string
    char* duplicate = (char*)malloc(len + 1); // Allocate memory for the duplicate

    if (duplicate == NULL) {
        return NULL; // Handle memory allocation failure
    }

    strcpy(duplicate, str); // Copy the original string to the duplicate
    return duplicate; // Return the duplicated string
}
```