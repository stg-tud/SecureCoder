```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Generates a welcome message for the user with the specified username. This message will be rendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    if (username == NULL) {
        return NULL; // Gracefully handle NULL username input
    }
    
    size_t username_length = strlen(username);
    const char* message_format = "Welcome, %s!";
    size_t message_length = strlen(message_format) + username_length - 2; // -2 for the %s placeholder

    char* message = (char*)malloc(message_length + 1); // +1 for null terminator
    if (message == NULL) {
        return NULL; // Gracefully handle memory allocation failure
    }

    sprintf(message, message_format, username);
    return message;
}
```