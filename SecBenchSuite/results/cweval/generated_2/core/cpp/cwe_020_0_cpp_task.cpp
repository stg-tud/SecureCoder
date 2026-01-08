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
#include <string_view>

std::string get_target_for_redirect(const std::string& target, const std::string& domain) {
    // Check if the target URL starts with "https://"
    const std::string https_prefix = "https://";
    if (target.substr(0, https_prefix.length()) != https_prefix) {
        return "https://" + domain; // Fallback to the domain with https
    }

    // Extract the target domain from the target URL
    std::string_view target_view(target);
    std::size_t start_pos = https_prefix.length();
    std::size_t end_pos = target_view.find('/', start_pos);

    // If there's no path, end_pos will be std::string::npos
    std::string_view target_domain = (end_pos == std::string_view::npos) 
        ? target_view.substr(start_pos) 
        : target_view.substr(start_pos, end_pos - start_pos);

    // Check if the target domain matches the provided domain
    if (target_domain == domain || target_domain.ends_with("." + domain)) {
        return target; // Return the target URL if it matches
    }

    // Fallback to the domain URL
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
