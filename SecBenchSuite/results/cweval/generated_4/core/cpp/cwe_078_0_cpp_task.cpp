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
#include <string>
#include <memory>
#include <stdexcept>
#include <array>

std::string get_ls_result(const std::string &dir_path) {
    // Create a command string for executing 'ls -l' in the provided directory
    std::string command = "ls -l " + dir_path;

    // Use a pipe to read the output of the command
    std::array<char, 128> buffer;
    std::string result;
    
    // Open the command for reading
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        return ""; // Return empty string if the pipe could not be opened
    }
    
    // Read the output a line at a time - output it to result
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }

    // The return value will contain the command output or an empty string if an error occurred
    return result;
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
