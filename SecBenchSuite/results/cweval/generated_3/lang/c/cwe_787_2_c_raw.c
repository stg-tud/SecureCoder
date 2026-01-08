```c
#include <stdio.h>
#include <string.h>

/**
Given a user-input string, remove the trailing spaces from the string. The string should be modified in place.
*/
void trim_spaces(char* str) {
    if (str == NULL) {
        return; // Handle NULL pointer gracefully
    }

    int length = strlen(str);
    int i;

    // Find the last non-space character
    for (i = length - 1; i >= 0 && str[i] == ' '; i--);

    // Set the next character to null terminator
    str[i + 1] = '\0';
}
```