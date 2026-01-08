```go
package main

import (
	"fmt"
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
	if strings.TrimSpace(subdomainPrefix) == "" || !isValidSubdomain(subdomainPrefix) {
		return fmt.Sprintf("https://%s", domain)
	}
	return fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)
}

// isValidSubdomain checks if the subdomain prefix is valid based on simple rules.
func isValidSubdomain(subdomain string) bool {
	parts := strings.Split(subdomain, ".")
	for _, part := range parts {
		if len(part) == 0 || len(part) > 63 || !isValidLabel(part) {
			return false
		}
	}
	return true
}

// isValidLabel checks if a label (part of the subdomain) adheres to DNS rules.
func isValidLabel(label string) bool {
	for _, char := range label {
		if !(('a' <= char && char <= 'z') || ('A' <= char && char <= 'Z') || ('0' <= char && char <= '9') || char == '-') {
			return false
		}
	}
	return true
}
```