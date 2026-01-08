```cpp
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
```