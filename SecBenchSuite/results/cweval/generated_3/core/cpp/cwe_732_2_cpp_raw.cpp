```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Create the full path for the secret file
    std::filesystem::path filePath = std::filesystem::path(directory) / filename;
    
    // Create the directory if it does not exist
    std::filesystem::create_directories(directory);
    
    // Open the file for writing
    std::ofstream outFile(filePath);
    if (!outFile) {
        std::cerr << "Error opening file for writing: " << filePath << std::endl;
        return;
    }
    
    // Write content to the file
    outFile << content;
    outFile.close();
    
    // Change the file permissions to make it accessible only by the current user
    int result = chmod(filePath.c_str(), S_IRUSR | S_IWUSR);
    if (result != 0) {
        std::cerr << "Error setting file permissions for: " << filePath << std::endl;
    }
}
```