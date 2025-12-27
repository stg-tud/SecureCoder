```cpp
#include <string>

bool searchPattern(const std::string& pattern, const std::string& content) {
    // Check if either the pattern or content is empty
    if (pattern.empty() || content.empty()) {
        return false;
    }
    
    // Use the find method to search for the pattern in the content
    std::size_t found = content.find(pattern);
    
    // If found, return true; otherwise, return false
    return found != std::string::npos;
}
```