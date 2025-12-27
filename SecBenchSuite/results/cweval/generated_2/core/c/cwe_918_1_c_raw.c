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
    // Check for NULL api_url or invalid user_id
    if (api_url == NULL || user_id == NULL || strlen(user_id) == 0) {
        return NULL;
    }
    
    // Calculate the length of the new URL
    size_t api_url_length = strlen(api_url);
    size_t user_id_length = strlen(user_id);
    
    // Allocate memory for the new URL
    char* full_url = (char*)malloc(api_url_length + user_id_length + 2); // +2 for '/' and '\0'
    
    // Check for allocation failure
    if (full_url == NULL) {
        return NULL;
    }
    
    // Construct the full URL
    strcpy(full_url, api_url);
    strcat(full_url, "/");
    strcat(full_url, user_id);
    
    return full_url;
}
```