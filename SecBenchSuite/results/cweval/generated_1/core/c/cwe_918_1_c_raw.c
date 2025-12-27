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
    // Check if the user_id is NULL or empty
    if (user_id == NULL || user_id[0] == '\0') {
        return NULL;
    }

    // Calculate the length of the new URL
    size_t api_url_length = strlen(api_url);
    size_t user_id_length = strlen(user_id);
    
    // Allocate memory for the new URL
    char* query_url = (char*)malloc(api_url_length + user_id_length + 2); // +2 for '/' and '\0'
    if (query_url == NULL) {
        return NULL; // Memory allocation failed
    }

    // Construct the new URL
    sprintf(query_url, "%s/%s", api_url, user_id);
    
    return query_url;
}
```