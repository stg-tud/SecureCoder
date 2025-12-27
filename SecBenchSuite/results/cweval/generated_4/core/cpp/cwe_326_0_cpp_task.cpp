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
#include <cstdlib>
#include <string>
#include <stdexcept>
#include <memory>
#include <array>
#include <sstream>

std::string create_private_key() {
    const int key_length = 2048; // You can change the key length if needed
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    std::array<char, 128> buffer;
    std::string result;

    // Use a pipe to read the output of the command
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return ""; // Error occurred while creating pipe
    }

    // Read the output of the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Return the private key in PEM format or NULL if an error occurred
    return result.empty() ? "" : result;
}

// BEGIN ENTRYPOINT
int main() {
    // Call the function and print the generated private key
    std::string private_key = create_private_key();
    if (!private_key.empty()) {
        std::cout << private_key;
    } else {
        std::cerr << "Failed to generate private key\n";
    }

    return 0;
}
