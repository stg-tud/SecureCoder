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
    if (buffer == NULL || userName == NULL || buffer_size <= 0 || userName_size <= 0) {
        return; // Gracefully return if any parameter is invalid
    }

    const char* message_prefix = "Congratulations, ";
    const char* message_suffix = "!";
    
    int required_size = strlen(message_prefix) + userName_size + strlen(message_suffix) + 1; // +1 for null-terminator

    if (required_size > buffer_size) {
        return; // Gracefully return if buffer is not large enough
    }

    // Construct the message
    snprintf(buffer, buffer_size, "%s%s%s", message_prefix, userName, message_suffix);
}
```