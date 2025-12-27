package main

import (
	"fmt"
	"os"
	"strings"
)

// getURLToVisit generates a URL to visit based on a trusted domain and a user-input subdomain prefix.
// If the subdomain is empty or invalid, it returns the domain itself.
func getURLToVisit(domain, subdomainPrefix string) string {
	if subdomainPrefix == "" || !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain
	}
	return fmt.Sprintf("https://%s.%s", subdomainPrefix, domain)
}

// isValidSubdomain checks if the provided subdomain is valid.
// A valid subdomain should consist of alphanumeric characters and hyphens,
// and should not start or end with a hyphen.
func isValidSubdomain(subdomain string) bool {
	parts := strings.Split(subdomain, ".")
	for _, part := range parts {
		if len(part) == 0 || len(part) > 63 || !isValidDomainPart(part) {
			return false
		}
	}
	return true
}

// isValidDomainPart checks if each part of the subdomain is valid according to DNS naming conventions.
func isValidDomainPart(part string) bool {
	return strings.IndexFunc(part, func(r rune) bool {
		return !(r >= '0' && r <= '9' || r >= 'a' && r <= 'z' || r >= 'A' && r <= 'Z' || r == '-')
	}) == -1 && !(strings.HasPrefix(part, "-") || strings.HasSuffix(part, "-"))
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <domain> <subdomain_prefix>\n", os.Args[0])
		os.Exit(1)
	}

	domain := os.Args[1]
	subdomainPrefix := os.Args[2]

	// Get the URL and print the result
	url := getURLToVisit(domain, subdomainPrefix)
	fmt.Print(url)
}
