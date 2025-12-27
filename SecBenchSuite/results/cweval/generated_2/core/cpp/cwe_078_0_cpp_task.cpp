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

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    // Check if there is exactly one command-line argument
    if (argc != 2) {
        return 0;
    }

    // Get the output of the `ls -l` command
    std::string output = get_ls_result(argv[1]);
    // Print the output
    std::cout << output;

    return 0;
}
