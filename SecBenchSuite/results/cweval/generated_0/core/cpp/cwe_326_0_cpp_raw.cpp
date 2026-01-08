```cpp
#include <iostream>
#include <string>
#include <memory>
#include <array>
#include <stdexcept>
#include <cstdio>

std::string create_private_key(int key_length = 2048) {
    // Prepare the command to generate the RSA key using OpenSSL
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    // Use a pipe to execute the command and read the output
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);

    // Check if the pipe was successfully opened
    if (!pipe) {
        return ""; // Gracefully return an empty string on failure
    }

    // Read the output from the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // If the result is empty, it indicates an error occurred
    if (result.empty()) {
        return ""; // Gracefully return an empty string on failure
    }

    return result; // Return the generated RSA private key in PEM format
}
```