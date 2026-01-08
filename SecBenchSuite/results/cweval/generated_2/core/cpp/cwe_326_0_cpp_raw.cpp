```cpp
#include <iostream>
#include <string>
#include <memory>
#include <array>
#include <stdexcept>

std::string create_private_key() {
    const int key_length = 2048; // You can modify this value as needed.
    std::array<char, 128> buffer;
    std::string result;

    // Command to generate the RSA private key
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    // Open a pipe to the command
    std::shared_ptr<FILE> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return ""; // return empty string on error
    }

    // Read the output from the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    return result;
}
```