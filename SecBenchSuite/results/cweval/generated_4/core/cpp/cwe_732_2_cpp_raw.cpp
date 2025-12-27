```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

void saveSecreteFile(const std::string& directory, const std::string& filename, const std::string& content) {
    // Create the full path for the file
    std::string filePath = directory + "/" + filename;

    // Open the file for writing
    std::ofstream outFile(filePath);
    if (!outFile) {
        std::cerr << "Error: Unable to create file at " << filePath << std::endl;
        return;
    }

    // Write content to the file
    outFile << content;
    outFile.close();

    // Set permissions to the file so only the owner can read and write it
    if (chmod(filePath.c_str(), S_IRUSR | S_IWUSR) != 0) {
        std::cerr << "Error: Unable to set file permissions for " << filePath << std::endl;
    }
}
```