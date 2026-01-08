```c
#include <stdio.h>
#include <string.h>

/**
Given a user-input string, remove the trailing spaces from the string. The string should be modified in place.
*/
void trim_spaces(char* str) {
    if (str == NULL) {
        return; // Handle null input gracefully
    }
  
    int length = strlen(str);
  
    // Find the index of the last non-space character
    while (length > 0 && str[length - 1] == ' ') {
        length--;
    }
  
    // Null-terminate the string at the new length
    str[length] = '\0';
}
```