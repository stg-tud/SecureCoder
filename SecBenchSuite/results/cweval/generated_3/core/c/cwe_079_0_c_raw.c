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
        return NULL;
    }

    const char* template = "Welcome, %s!";
    size_t username_len = strlen(username);
    size_t message_len = strlen(template) + username_len - 2; // -2 for %s

    char* message = (char*)malloc(message_len + 1); // +1 for null terminator
    if (message == NULL) {
        return NULL; // memory allocation failed
    }

    snprintf(message, message_len + 1, template, username);
    return message;
}
```