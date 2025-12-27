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
    int index = length - 1;

    // Move backwards through the string to find the last non-space character
    while (index >= 0 && str[index] == ' ') {
        index--;
    }

    // Null-terminate the string at the new end
    str[index + 1] = '\0';
}
```