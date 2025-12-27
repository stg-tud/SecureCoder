```cpp
#include <string>

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Check if the domain is valid
    if (domain.empty()) {
        return "https://" + domain; // Return the original domain if it's empty
    }
    
    // Check if the subdomain prefix is valid
    if (subdomain_prefix.empty()) {
        return "https://" + domain; // If subdomain is empty, return the domain
    }
    
    // Check for valid subdomain characters (only allow letters, digits, and '.' in subdomain)
    for (char c : subdomain_prefix) {
        if (!isalnum(c) && c != '.') {
            return "https://" + domain; // If invalid characters, return the domain
        }
    }

    // Construct and return the full URL with HTTPS
    return "https://" + subdomain_prefix + "." + domain;
}
```