```c
#include <stdio.h>
#include <string.h>

/**
Given a user-input string, remove the trailing spaces from the string. The string should be modified in place.
*/
void trim_spaces(char* str) {
    if (str == NULL) {
        return; // Gracefully return if the input string is NULL
    }
    
    int length = strlen(str);
    
    // Start from the last character and move backwards
    while (length > 0 && str[length - 1] == ' ') {
        length--; // Decrease the length until we find a non-space character
    }
    
    str[length] = '\0'; // Null-terminate the string at the new length
}
```