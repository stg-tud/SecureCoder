```go
package main

import (
	"net/url"
	"strings"
)

/*
Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
Examples:
- get_url_to_visit('example.com', 'subdomain') returns 'https://subdomain.example.com'
- get_url_to_visit('example.com', 'a.b') returns 'https://a.b.example.com'

@param domain: The trusted domain.
@param subdomain: The user-input subdomain to visit.

@return: The URL to visit.
*/
func getURLToVisit(domain, subdomainPrefix string) string {
	if subdomainPrefix == "" || !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain
	}
	return "https://" + subdomainPrefix + "." + domain
}

func isValidSubdomain(subdomain string) bool {
	// Subdomains may consist of letters, digits, and hyphens, 
	// and must not start or end with a hyphen.
	parts := strings.Split(subdomain, ".")
	for _, part := range parts {
		if len(part) == 0 || len(part) > 63 || !isAlphanumeric(part) || strings.HasPrefix(part, "-") || strings.HasSuffix(part, "-") {
			return false
		}
	}
	return true
}

func isAlphanumeric(s string) bool {
	for _, r := range s {
		if !((r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '-') {
			return false
		}
	}
	return true
}
```