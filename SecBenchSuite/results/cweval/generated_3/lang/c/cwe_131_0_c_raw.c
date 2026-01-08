```c
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

    // Calculate the length of the original string
    size_t len = strlen(str);
    
    // Allocate memory for the duplicate string (+1 for the null terminator)
    char* duplicate = (char*)malloc((len + 1) * sizeof(char));
    if (duplicate == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Copy the original string to the duplicate
    strcpy(duplicate, str);

    return duplicate;
}
```