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
        return NULL; // Gracefully handle NULL username
    }

    // Calculate the length of the welcome message
    const char* message_format = "Welcome, %s!";
    int message_length = snprintf(NULL, 0, message_format, username) + 1; // +1 for the null terminator
    
    // Allocate memory for the welcome message
    char* welcome_message = (char*)malloc(message_length);
    if (welcome_message == NULL) {
        return NULL; // Gracefully handle memory allocation failure
    }

    // Create the welcome message
    snprintf(welcome_message, message_length, message_format, username);

    return welcome_message;
}
```