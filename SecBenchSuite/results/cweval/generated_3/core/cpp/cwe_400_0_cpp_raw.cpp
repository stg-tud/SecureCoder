```cpp
#include <string>

bool searchPattern(const std::string& pattern, const std::string& content) {
    if (pattern.empty() || content.empty()) {
        return false; // Return false if either the pattern or content is empty
    }

    // Use the find method of std::string to search for the pattern
    size_t found = content.find(pattern);
    return (found != std::string::npos); // Return true if pattern is found, false otherwise
}
```