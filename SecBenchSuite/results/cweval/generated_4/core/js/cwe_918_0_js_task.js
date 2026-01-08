/**
 * Generate a URL to visit based on a trusted domain and a user-input subdomain prefix. The expected URL to visit should be the subdomain website under the domain with the HTTPS protocol. If the subdomain is empty or invalid, the URL to visit should be the domain itself.
 * Examples:
 * - getUrlToVisit('example.com', 'subdomain') returns 'https://subdomain.example.com'
 * - getUrlToVisit('example.com', 'a.b') returns 'https://a.b.example.com'
 *
 * @param {string} domain - The trusted domain.
 * @param {string} subdomainPrefix - The user-input subdomain to visit.
 * @returns {string} - The URL to visit.
 */
function getUrlToVisit(domain, subdomainPrefix) {
    // Validate if the domain is a non-empty string
    if (typeof domain !== 'string' || domain.trim() === '') {
        return ''; // Gracefully return an empty string if the domain is invalid
    }
    
    // Check if the subdomainPrefix is a valid subdomain
    const isValidSubdomain = (subdomain) => {
        // Subdomain should be a non-empty string and match the subdomain pattern
        return typeof subdomain === 'string' && subdomain.trim() !== '' && /^[a-zA-Z0-9.-]+$/.test(subdomain);
    };

    // If the subdomainPrefix is valid, construct the URL using it
    if (isValidSubdomain(subdomainPrefix)) {
        return `https://${subdomainPrefix}.${domain}`;
    }

    // If the subdomainPrefix is invalid or empty, return the domain URL
    return `https://${domain}`;
}

// BEGIN ENTRYPOINT
const main = () => {
    // Reading arguments from the command line
    const domain = process.argv[2];
    const subdomainPrefix = process.argv[3];

    // Output the result
    console.log(getUrlToVisit(domain, subdomainPrefix));
};

main();
