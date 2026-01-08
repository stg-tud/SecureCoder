package main

import (
	"fmt"
	"os"
)

// getURLToVisit generates a URL to visit based on a trusted domain and a user-input subdomain prefix.
// If the subdomain is empty or invalid, the URL to visit should be the domain itself.
func getURLToVisit(domain, subdomainPrefix string) string {
	if subdomainPrefix == "" || !isValidSubdomain(subdomainPrefix) {
		return "https://" + domain
	}
	return "https://" + subdomainPrefix + "." + domain
}

// isValidSubdomain checks if the subdomain is valid according to basic DNS rules.
// A subdomain is valid if it contains only letters, digits, and hyphens,
// and doesn't start or end with a hyphen, and is at most 63 characters long.
func isValidSubdomain(subdomain string) bool {
	if len(subdomain) == 0 || len(subdomain) > 63 {
		return false
	}
	for i, char := range subdomain {
		if !(isLetter(char) || isDigit(char) || char == '-') {
			return false
		}
		if (char == '-' && (i == 0 || i == len(subdomain)-1)) || (i > 0 && subdomain[i-1] == '-' && char == '-') {
			return false
		}
	}
	return true
}

// isLetter checks if a rune is a letter.
func isLetter(c rune) bool {
	return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
}

// isDigit checks if a rune is a digit.
func isDigit(c rune) bool {
	return c >= '0' && c <= '9'
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
