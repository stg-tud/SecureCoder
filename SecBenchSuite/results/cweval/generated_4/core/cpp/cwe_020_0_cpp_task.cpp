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
#include <iostream>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Ensure the domain is prefixed with "https://"
    std::string fallback_url = "https://" + domain;

    // Check if the target URL starts with "https://" and contains the domain
    if (target.find("https://") == 0 && target.find(domain) != std::string::npos) {
        return target; // Return the target URL if it matches the domain
    }

    return fallback_url; // Fallback to the domain URL
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
