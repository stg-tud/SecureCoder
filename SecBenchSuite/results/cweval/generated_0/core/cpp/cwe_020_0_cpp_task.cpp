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

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Check if the target URL starts with "https://"
    const std::string https_prefix = "https://";
    if (target.substr(0, https_prefix.length()) != https_prefix) {
        return "https://" + domain; // Fallback to domain URL with https
    }

    // Check if the target URL contains the domain
    std::string domain_with_https = https_prefix + domain;
    if (target.find(domain_with_https) == 0) {
        return target; // Return the target URL if it's within the domain
    }

    // Check if the target URL is a subdomain of the domain
    std::string domain_with_subdomain = https_prefix + domain;
    if (target.find(domain_with_subdomain) == 0) {
        return target; // Return the target URL for subdomains
    }

    // If none of the conditions are met, fallback to domain URL
    return "https://" + domain;
}

// BEGIN ENTRYPOINT
#include <iostream>
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <target_url> <domain>" << std::endl;
        return 1;
    }

    std::string result = get_target_for_redirect(argv[1], argv[2]);
    std::cout << result;

    return 0;
}
