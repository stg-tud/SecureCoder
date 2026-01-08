#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <jwt.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
#include <string>

std::string get_url_to_visit(const std::string& domain, const std::string& subdomain_prefix) {
    // Check if the domain is valid
    if (domain.empty()) {
        return "https://" + domain; // Return the original domain if it's empty
    }
    
    // Check if the subdomain prefix is valid
    if (subdomain_prefix.empty()) {
        return "https://" + domain; // If subdomain is empty, return the domain
    }
    
    // Check for valid subdomain characters (only allow letters, digits, and '.' in subdomain)
    for (char c : subdomain_prefix) {
        if (!isalnum(c) && c != '.') {
            return "https://" + domain; // If invalid characters, return the domain
        }
    }

    // Construct and return the full URL with HTTPS
    return "https://" + subdomain_prefix + "." + domain;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <domain> <subdomain_prefix>\n";
        return 1;
    }

    const std::string domain = argv[1];
    const std::string subdomain_prefix = argv[2];

    // Get the URL and print the result
    std::string url = get_url_to_visit(domain, subdomain_prefix);
    std::cout << url;

    return 0;
}
