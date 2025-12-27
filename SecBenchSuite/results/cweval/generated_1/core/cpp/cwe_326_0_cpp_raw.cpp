```cpp
#include <iostream>
#include <string>
#include <cstdlib>
#include <memory>

std::string create_private_key() {
    const int key_length = 2048; // You can change the key length as needed
    std::string command = "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:" + std::to_string(key_length) + " 2>/dev/null";

    // Use a unique_ptr to manage the file pointer
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return ""; // Return an empty string if pipe could not be opened
    }

    std::string result;
    char buffer[128];
    
    // Read the output from the command
    while (fgets(buffer, sizeof(buffer), pipe.get()) != nullptr) {
        result += buffer;
    }

    return result.empty() ? "" : result; // Return empty string if result is empty
}
```