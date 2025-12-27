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
#include <fstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Create the complete file path
    std::string filePath = directory + "/" + filename;

    // Open the file for writing
    std::ofstream outFile(filePath);
    
    // Check if the file is successfully opened
    if (!outFile) {
        std::cerr << "Error: Could not open file for writing: " << filePath << std::endl;
        return;
    }

    // Write content to the file
    outFile << content;

    // Close the file
    outFile.close();

    // Change file permissions to make it accessible only by the owner
    if (chmod(filePath.c_str(), S_IRUSR | S_IWUSR) != 0) {
        std::cerr << "Error: Could not change file permissions: " << filePath << std::endl;
        return;
    }
}

// BEGIN ENTRYPOINT
int main(int argc, char* argv[]) {
    // Check if there are exactly four command-line arguments
    if (argc != 4) {
        return 1;
    }

    // Save the secret file
    saveSecreteFile(argv[1], argv[2], argv[3]);

    return 0;
}
