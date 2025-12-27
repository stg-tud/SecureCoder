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
        return NULL; // Gracefully handle NULL input
    }

    size_t len = strlen(str);
    char* duplicate = (char*)malloc((len + 1) * sizeof(char)); // Allocate memory for the duplicate

    if (duplicate == NULL) {
        return NULL; // Gracefully handle memory allocation failure
    }

    strcpy(duplicate, str); // Copy the string into the newly allocated memory
    return duplicate; // Return the duplicated string
}
```