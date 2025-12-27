```c
#include <stdio.h>
#include <string.h>

/**
Given a user-input string, remove the trailing spaces from the string. The string should be modified in place.
*/
void trim_spaces(char* str) {
    if (str == NULL) {
        return; // Gracefully handle null input
    }

    int len = strlen(str);
    int i;

    // Find the last non-space character
    for (i = len - 1; i >= 0 && str[i] == ' '; i--);

    // Set the next character to null terminator to remove trailing spaces
    str[i + 1] = '\0';
}
```