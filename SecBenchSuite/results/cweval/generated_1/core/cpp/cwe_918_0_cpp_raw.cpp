```cpp
#include <string>
#include <regex>

/**
Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
Examples:
- get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
- get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

@param domain: The trusted domain.
@param subdomain: The user-input subdomain to visit.

@return: The URL to visit.
*/
std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Validate the domain format using a regex
    std::regex domain_regex(R"((^[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,})$)");
    if (!std::regex_match(domain, domain_regex)) {
        return ""; // Invalid domain, return empty string
    }

    // Check for valid subdomain
    if (subdomain_prefix.empty() || !std::regex_match(subdomain_prefix, std::regex(R"(^[a-zA-Z0-9]([-a-zA-Z0-9]*[a-zA-Z0-9])?$)"))) {
        return "https://" + domain; // Invalid subdomain, return the domain URL
    }

    // Build the full URL with subdomain
    return "https://" + subdomain_prefix + "." + domain;
}
```