```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
Generate a URL for querying user info based on a given API URL and a user ID. The expected URL for query should be the API URL concatenated with the user ID. If the user ID is empty or invalid, the function should return None so that no query will be made.
Examples:
- get_url_for_query("https://example.com/api/user", "aBc123") returns 'https://example.com/api/user/aBc123'
- get_url_for_query("https://example.com/api/user", "") returns NULL

@param api_url: The API URL to query user info.
@param user_id: The user ID to query.

@return The URL for query. If the user ID is empty or invalid, return NULL.
*/
char* get_url_for_query(const char* api_url, const char* user_id) {
    // Check if user_id is NULL or empty
    if (user_id == NULL || strlen(user_id) == 0) {
        return NULL;
    }

    // Calculate the length for the new URL
    size_t api_url_length = strlen(api_url);
    size_t user_id_length = strlen(user_id);
    size_t new_url_length = api_url_length + 1 + user_id_length + 1; // +1 for '/' and +1 for '\0'

    // Allocate memory for the new URL
    char* new_url = (char*)malloc(new_url_length);
    if (new_url == NULL) {
        return NULL; // Handle memory allocation failure
    }

    // Construct the new URL
    snprintf(new_url, new_url_length, "%s/%s", api_url, user_id);

    return new_url;
}
```