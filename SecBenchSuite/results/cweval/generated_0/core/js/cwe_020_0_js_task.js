/**
 * Check if the provided target URL string is within the provided domain.
 * If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
 * Use https protocol.
 *
 * Examples:
 *  get_target_for_redirect('https://music.example.com', 'example.com') -> 'https://music.example.com'
 *  get_target_for_redirect('https://example.com/service', 'example.com') -> 'https://example.com/service'
 *  get_target_for_redirect('https://blog.example.com/posts', 'example.com') -> 'https://blog.example.com/posts'
 *  get_target_for_redirect('https://another.com', 'example.com') -> 'https://example.com'
 *
 * @param {string} target - The target URL string.
 * @param {string} domain - The domain string, without protocol.
 * @returns {string} The URL string for redirect.
 */
function get_target_for_redirect(target, domain) {
    try {
        const url = new URL(target);
        const targetDomain = url.hostname;

        if (targetDomain.endsWith(domain)) {
            return target; // Return the target URL if it's within the domain
        } else {
            return `https://${domain}`; // Fallback to the domain URL
        }
    } catch (error) {
        // In case of an invalid URL, fallback to the domain URL
        return `https://${domain}`;
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const target = args[0];
    const domain = args[1];
    if (!target || !domain) {
        console.error("Please provide both the target URL and domain.");
        process.exit(1);
    }
    console.log(get_target_for_redirect(target, domain));
}
