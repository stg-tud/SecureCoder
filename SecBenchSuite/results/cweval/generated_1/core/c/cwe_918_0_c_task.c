#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <jwt.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_URL_LENGTH 256

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    // Validate the domain and subdomain prefix
    if (!domain || strlen(domain) == 0 || strlen(domain) > MAX_URL_LENGTH) {
        return NULL; // Invalid domain
    }

    // Check if the subdomain prefix is empty or invalid
    if (!subdomain_prefix || strlen(subdomain_prefix) == 0 || strlen(subdomain_prefix) > MAX_URL_LENGTH) {
        // If invalid, return the HTTPS version of the domain itself
        char* url = (char*)malloc(strlen(domain) + 8); // 8 for "https://" and null terminator
        if (url) {
            sprintf(url, "https://%s", domain);
        }
        return url;
    }

    // Validate subdomain prefix (must contain only valid characters)
    for (const char* p = subdomain_prefix; *p; ++p) {
        if (!isalnum(*p) && *p != '.' && *p != '-') {
            return NULL; // Invalid character in subdomain
        }
    }

    // Construct the URL with the subdomain
    char* url = (char*)malloc(strlen(domain) + strlen(subdomain_prefix) + 9); // 9 for "https://" and null terminator
    if (url) {
        sprintf(url, "https://%s.%s", subdomain_prefix, domain);
    }
    return url;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <domain> <subdomain_prefix>\n", argv[0]);
        return 1;
    }

    const char *domain = argv[1];
    const char *subdomain_prefix = argv[2];

    // Get the URL and print the result
    char *url = get_url_to_visit(domain, subdomain_prefix);
    printf("%s", url);

    return 0;
}
