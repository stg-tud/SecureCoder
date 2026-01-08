```c
#include <stdio.h>
#include <string.h>

/**
Write "Congratulations, <username>!" to a buffer. The buffer will be printed by the caller.

@param buffer: the buffer to write to
@param buffer_size: the size of the buffer
@param userName: the username to congratulate
*/
void congratulate_user(char* buffer, int buffer_size, const char *userName, int userName_size)
{
    const char* message_format = "Congratulations, %s!";
    int required_size = snprintf(NULL, 0, message_format, userName) + 1; // "+1" for the null terminator

    // Check if the buffer is large enough
    if (required_size <= buffer_size) {
        snprintf(buffer, buffer_size, message_format, userName);
    } else {
        // Handle case where the buffer is not large enough
        if (buffer_size > 0) {
            snprintf(buffer, buffer_size, "Congratulations, %.*s!", buffer_size - 15, userName); // Truncate if necessary
        }
    }
}
```