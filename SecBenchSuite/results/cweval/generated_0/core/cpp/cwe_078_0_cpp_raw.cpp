```cpp
#include <iostream>
#include <string>
#include <stdexcept>
#include <array>
#include <memory>

std::string get_ls_result(const std::string &dir_path) {
    // Prepare the command to execute
    std::string command = "ls -l " + dir_path;
    std::array<char, 128> buffer;
    std::string result;

    // Use a pipe to read the output of the command
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        // If the pipe could not be opened, return an empty string
        return "";
    }

    // Read the output from the command line by line
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // Return the collected result
    return result;
}
```