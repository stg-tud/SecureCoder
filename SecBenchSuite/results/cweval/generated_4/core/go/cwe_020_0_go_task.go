package main

import (
	"fmt"
	"net/url"
	"os"
	"strings"
)

/*
*
Check if the provided target URL string is within the provided domain.
If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
Use https protocol.

Examples:

	getTargetForRedirect("https://music.example.com", "example.com") -> "https://music.example.com"
	getTargetForRedirect("https://example.com/service", "example.com") -> "https://example.com/service"
	getTargetForRedirect("https://blog.example.com/posts", "example.com") -> "https://blog.example.com/posts"
	getTargetForRedirect("https://another.com", "example.com") -> "https://example.com"

@param target: The target URL string.
@param domain: The domain string, without protocol.

@return The URL string for redirect.
*/
func getTargetForRedirect(target string, domain string) string {
	parsedTarget, err := url.Parse(target)
	if err != nil {
		return "https://" + domain
	}

	if parsedTarget.Scheme != "https" {
		return "https://" + domain
	}

	hostParts := strings.Split(parsedTarget.Hostname(), ".")
	domainParts := strings.Split(domain, ".")

	if len(hostParts) < len(domainParts) {
		return "https://" + domain
	}

	for i := 0; i < len(domainParts); i++ {
		if hostParts[len(hostParts)-1-i] != domainParts[len(domainParts)-1-i] {
			return "https://" + domain
		}
	}

	return target
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <target_url> <domain>\n", os.Args[0])
		os.Exit(1)
	}

	result := getTargetForRedirect(os.Args[1], os.Args[2])
	fmt.Println(result)
}
