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
    const char* message_format = "Congratulations, ";
    const char* message_suffix = "!";
    
    // Ensure we have enough space for the message
    int total_length = strlen(message_format) + userName_size + strlen(message_suffix);
    
    if (total_length >= buffer_size) {
        // If the buffer is too small, return gracefully without writing.
        return;
    }
    
    // Construct the full message
    snprintf(buffer, buffer_size, "%s%s%s", message_format, userName, message_suffix);
}
```