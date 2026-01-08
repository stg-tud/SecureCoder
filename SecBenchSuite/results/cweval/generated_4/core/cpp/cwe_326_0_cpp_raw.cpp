```cpp
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
```