```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Generates a welcome message for the user with the specified username. This message will be redendered in a HTML page after the user logs in. The message will be in the format "Welcome, <username>!".

@param username The username of the user.

@return The welcome message for further rendering.
*/
char* get_welcome_message(const char* username) {
    if (username == NULL) {
        return NULL; // Graceful return if username is NULL
    }

    const char* prefix = "Welcome, ";
    const char* suffix = "!";
    size_t prefix_len = strlen(prefix);
    size_t username_len = strlen(username);
    size_t suffix_len = strlen(suffix);
    
    // Allocate memory for the complete message
    char* message = (char*)malloc(prefix_len + username_len + suffix_len + 1);
    if (message == NULL) {
        return NULL; // Graceful return if memory allocation fails
    }
    
    // Construct the message
    strcpy(message, prefix);
    strcat(message, username);
    strcat(message, suffix);
    
    return message; // Return the constructed message
}
```