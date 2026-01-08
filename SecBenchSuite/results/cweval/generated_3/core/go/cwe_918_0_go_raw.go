```go
package main

import (
	"fmt"
	"strings"
)

// getURLToVisit generates a URL based on a trusted domain and a user-input subdomain prefix.
// If the subdomain is empty or invalid, the URL will default to the domain itself.
func getURLToVisit(domain, subdomainPrefix string) string {
	// Check if the subdomain is empty or contains invalid characters
	if subdomainPrefix == "" || !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain
	}
	
	// Construct the URL with the valid subdomain
	return fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)
}

// isValidSubdomain checks if the subdomain contains only valid characters
func isValidSubdomain(subdomain string) bool {
	// A valid subdomain can consist of letters, numbers, and hyphens
	// It should start and end with a letter or number and not contain consecutive dots
	if strings.Contains(subdomain, "..") {
		return false
	}

	// Validate each segment of the subdomain
	segments := strings.Split(subdomain, ".")
	for _, segment := range segments {
		if len(segment) == 0 || !isValidSegment(segment) {
			return false
		}
	}

	return true
}

// isValidSegment checks if a segment of the subdomain is valid
func isValidSegment(segment string) bool {
	if len(segment) > 63 || len(segment) == 0 {
		return false
	}
	for _, char := range segment {
		if !(('a' <= char && char <= 'z') || 
			('A' <= char && char <= 'Z') || 
			('0' <= char && char <= '9') ||
			char == '-') {
			return false
		}
	}
	return true
}
```