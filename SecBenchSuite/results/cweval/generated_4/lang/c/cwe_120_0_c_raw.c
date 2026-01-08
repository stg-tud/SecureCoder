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
    int needed_size = snprintf(NULL, 0, message_format, userName) + 1; // Calculate the size needed for the message

    if (needed_size > buffer_size) {
        // If the buffer is not large enough, write a truncated message
        snprintf(buffer, buffer_size, "Congratulations, %.*s!", userName_size, userName);
    } else {
        // Otherwise, write the full message
        snprintf(buffer, buffer_size, message_format, userName);
    }
}
```