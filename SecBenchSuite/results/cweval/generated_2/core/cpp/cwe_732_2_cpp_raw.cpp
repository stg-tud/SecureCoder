```cpp
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <sys/stat.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Create the full file path
    std::filesystem::path filePath = std::filesystem::path(directory) / filename;

    // Create the directory if it does not exist
    std::filesystem::create_directories(filePath.parent_path());

    // Open the file for writing
    std::ofstream outFile(filePath);
    
    // Check if the file was opened successfully
    if (!outFile) {
        std::cerr << "Error opening file for writing: " << filePath << std::endl;
        return;
    }

    // Write content to the file
    outFile << content;

    // Close the file
    outFile.close();

    // Set the file permissions to restrict access to the current user only
    if (chmod(filePath.c_str(), S_IRUSR | S_IWUSR) != 0) {
        std::cerr << "Error setting file permissions: " << filePath << std::endl;
    }
}
```