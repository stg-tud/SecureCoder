```cpp
#include <iostream>
#include <sstream>
#include <string>
#include <memory>
#include <array>

std::string get_ls_result(const std::string &dir_path) {
    // Command to be executed
    std::string command = "ls -l " + dir_path;

    // Create a pipe to read the command output
    std::array<char, 128> buffer;
    std::string result;
    
    // Use popen to execute the command and read the output
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return ""; // Return empty string if pipe creation failed
    }

    // Read the output from the command
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Return the result or an empty string if there was an error
    return result.empty() ? "" : result;
}
```