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
    const char* message_prefix = "Congratulations, ";
    const char* message_suffix = "!";
    int required_length = strlen(message_prefix) + userName_size + strlen(message_suffix);
    
    // Check if the buffer is large enough to hold the message
    if (buffer_size <= 0 || buffer == NULL || required_length >= buffer_size) {
        // Gracefully return without writing to the buffer
        return;
    }
    
    // Construct the message
    snprintf(buffer, buffer_size, "%s%s%s", message_prefix, userName, message_suffix);
}
```