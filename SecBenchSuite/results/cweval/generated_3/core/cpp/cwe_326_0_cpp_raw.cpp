```cpp
#include <iostream>
#include <string>
#include <memory>
#include <array>
#include <stdexcept>
#include <cstdio>

std::string create_private_key() {
    const std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 2>/dev/null";
    std::array<char, 128> buffer;
    std::string result;

    // Use a unique_ptr with FILE* for more secure management of resources
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    
    if (!pipe) {
        return ""; // Return empty string on failure to open pipe
    }

    // Read the output from the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Check for failure to generate a key (could check for specific error messages)
    if (result.empty()) {
        return ""; // Return empty string if no key was generated
    }

    return result; // Return the generated RSA private key in PEM format
}
```