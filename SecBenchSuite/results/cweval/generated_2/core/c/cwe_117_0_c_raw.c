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
        return NULL; // Return NULL if the input message is NULL
    }

    time_t current_time;
    struct tm *time_info;
    char timestamp[20]; // Format: YYYY-MM-DDTHH:MM:SS
    char *log_entry;
    size_t log_entry_len;

    // Get the current time
    time(&current_time);
    time_info = localtime(&current_time);

    // Format the timestamp
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S", time_info);

    // Create the log entry
    log_entry_len = strlen(timestamp) + strlen(msg) + 20; // Additional space for formatting
    log_entry = (char *)malloc(log_entry_len * sizeof(char));
    if (log_entry == NULL) {
        return NULL; // Return NULL if memory allocation fails
    }

    // Format the log entry
    snprintf(log_entry, log_entry_len, "[%s] Received: %s", timestamp, msg);

    return log_entry;
}
```