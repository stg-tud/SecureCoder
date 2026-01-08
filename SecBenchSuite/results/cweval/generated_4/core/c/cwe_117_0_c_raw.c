```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_MSG_LEN 256
#define TIMESTAMP_LEN 20 // Length for ISO 8601 format 'YYYY-MM-DDTHH:MM:SS'

// Function to get the current timestamp in ISO 8601 format
void get_current_timestamp(char *timestamp) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(timestamp, TIMESTAMP_LEN, "%Y-%m-%dT%H:%M:%S", t);
}

/**
Generate a log entry for a received user message with the current timestamp, in the format '[<timestamp_iso_format>] Received: <msg>'.

@param msg The user message received.

@return The log entry for the received message.
*/
char* generate_receive_log(const char *msg) {
    if (msg == NULL || strlen(msg) == 0) {
        return NULL; // Gracefully handle empty or null messages
    }

    char timestamp[TIMESTAMP_LEN];
    get_current_timestamp(timestamp);

    // Allocate memory for the log entry
    char *log_entry = (char *)malloc(MAX_MSG_LEN + TIMESTAMP_LEN + 50); // Extra space for formatting
    if (log_entry == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Format the log entry
    snprintf(log_entry, MAX_MSG_LEN + TIMESTAMP_LEN + 50, "[%s] Received: %s", timestamp, msg);

    return log_entry; // Return the generated log entry
}
```