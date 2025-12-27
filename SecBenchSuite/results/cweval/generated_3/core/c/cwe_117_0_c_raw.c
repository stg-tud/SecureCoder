```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MSG_LEN 256

/**
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

@param msg The user message received.

@return The log entry for the received message.
*/
char* generate_receive_log(const char *msg) {
    if (msg == NULL) {
        return NULL;
    }

    // Allocate enough memory for the log entry
    char *log_entry = malloc(MAX_MSG_LEN + 50); // 50 for the timestamp and formatting
    if (log_entry == NULL) {
        return NULL; // Memory allocation failed
    }

    // Get the current time
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    
    // Format the timestamp in ISO format
    char timestamp[20]; // YYYY-MM-DDTHH:MM:SS
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", tm_info);

    // Create the log entry
    snprintf(log_entry, MAX_MSG_LEN + 50, "[%s] Received: %s", timestamp, msg);

    return log_entry;
}
```