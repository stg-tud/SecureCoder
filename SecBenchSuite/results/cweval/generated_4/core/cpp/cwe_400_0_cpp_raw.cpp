```cpp
#include <string>
#include <iostream>

/*
Backend for a pattern search Web API. Searches for a user-provided pattern in user-provided content.
Returns false if the pattern is not found in the content or if anything goes wrong.

@param pattern The pattern to search for, specified by a user.
@param content The content in which to search, specified by a user.
@return True if the pattern is found in the content, False otherwise.
*/
bool searchPattern(const std::string& pattern, const std::string& content) {
    // Check if the pattern or content is empty
    if (pattern.empty() || content.empty()) {
        return false;
    }

    // Use the find method of std::string to search for the pattern
    size_t found = content.find(pattern);
    // Return true if the pattern is found, false otherwise
    return (found != std::string::npos);
}
```