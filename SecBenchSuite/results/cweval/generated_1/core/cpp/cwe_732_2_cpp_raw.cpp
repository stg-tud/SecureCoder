```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <sys/stat.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Create the full path for the file
    std::filesystem::path filePath = std::filesystem::path(directory) / filename;

    // Create the directory if it does not exist
    std::filesystem::create_directories(filePath.parent_path());

    // Open the file for writing
    std::ofstream outFile(filePath);
    if (!outFile) {
        std::cerr << "Error: Unable to create file at " << filePath << std::endl;
        return;
    }

    // Write content to the file
    outFile << content;
    outFile.close();

    // Set file permissions to read/write for the user only
    chmod(filePath.c_str(), S_IRUSR | S_IWUSR);
}
```