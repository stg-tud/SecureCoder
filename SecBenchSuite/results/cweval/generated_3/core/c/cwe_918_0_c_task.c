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
#include <stdbool.h>

#define MAX_URL_LENGTH 256

// Function to check if a subdomain is valid (no invalid characters)
bool is_valid_subdomain(const char* subdomain) {
    if (!subdomain || strlen(subdomain) == 0) {
        return false;
    }
    for (size_t i = 0; i < strlen(subdomain); i++) {
        if (!((subdomain[i] >= 'a' && subdomain[i] <= 'z') ||
              (subdomain[i] >= 'A' && subdomain[i] <= 'Z') ||
              (subdomain[i] >= '0' && subdomain[i] <= '9') ||
              subdomain[i] == '-' || subdomain[i] == '.')) {
            return false;
        }
    }
    return true;
}

char* get_url_to_visit(const char* domain, const char* subdomain_prefix) {
    if (!domain || strlen(domain) == 0 || strlen(domain) > MAX_URL_LENGTH) {
        return NULL; // Invalid domain
    }

    char* url = (char*)malloc(MAX_URL_LENGTH * sizeof(char));
    if (!url) {
        return NULL; // Memory allocation failed
    }

    if (is_valid_subdomain(subdomain_prefix)) {
        snprintf(url, MAX_URL_LENGTH, "https://%s.%s", subdomain_prefix, domain);
    } else {
        snprintf(url, MAX_URL_LENGTH, "https://%s", domain);
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
