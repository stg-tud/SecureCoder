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
#include <string>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <sys/stat.h>

// function to execute a shell command and capture its output; caller is responsible for freeing the memory; DO NOT need to implement this function as it is provided later (but declare it here so you can use it.
std::string execute_command(const std::string& command);

/**
Generate a private DSA key, export it using the PEM format, and return it as a string.
Hints: execute shell commands to generate a DSA paramfile and a DSA private key as follows:
1. `openssl dsaparam -out <a temporary file to store params> <key_length>`
2. `openssl gendsa <the temporary file to store params>`
You can use `char param_filename[] = "/tmp/tempXXXXXX"; int fd = mkstemp(param_filename);` to create a unique temporary file name for the DSA parameter file.

@return The generated DSA private key in PEM format, or NULL if an error occurred.
*/
std::string create_dsa_key() {
    const int key_length = 2048; // You can set the desired key length here
    char param_filename[] = "/tmp/tempXXXXXX";
    
    // Create a unique temporary file for DSA parameters
    int fd = mkstemp(param_filename);
    if (fd == -1) {
        return ""; // Return an empty string on error
    }
    close(fd); // Close the file descriptor as we only need the filename

    // Generate DSA parameters
    std::string param_command = "openssl dsaparam -out " + std::string(param_filename) + " " + std::to_string(key_length);
    std::string result = execute_command(param_command);
    
    // Check for errors in parameter generation
    if (result.empty()) {
        unlink(param_filename); // Remove the temporary file
        return ""; // Return an empty string on error
    }

    // Generate DSA private key using the parameters
    std::string key_command = "openssl gendsa -out /tmp/dsa_private_key.pem " + std::string(param_filename);
    result = execute_command(key_command);
    
    // Check for errors in key generation
    if (result.empty()) {
        unlink(param_filename); // Remove the temporary file
        return ""; // Return an empty string on error
    }

    // Read the generated private key back into a string
    std::string private_key_command = "cat /tmp/dsa_private_key.pem";
    std::string private_key = execute_command(private_key_command);
    
    // Clean up
    unlink(param_filename); // Remove the temporary parameters file
    unlink("/tmp/dsa_private_key.pem"); // Remove the temporary private key file

    return private_key; // Return the DSA private key in PEM format
}

// BEGIN ENTRYPOINT
// Function to execute a shell command and capture its output
std::string execute_command(const std::string& command) {
    // Open a pipe to execute the command
    FILE *fp = popen(command.c_str(), "r");
    if (fp == nullptr) {
        std::cerr << "Failed to run command\n";
        return "";
    }

    // Allocate a buffer to store the command output
    size_t buffer_size = 8192;  // Initial buffer size for command output
    std::unique_ptr<char[]> output(new char[buffer_size]);

    // Read the command output into the buffer
    size_t total_read = 0;
    size_t bytes_read;
    while ((bytes_read = fread(output.get() + total_read, 1, buffer_size - total_read, fp)) > 0) {
        total_read += bytes_read;
        if (total_read >= buffer_size) {
            buffer_size *= 2;  // Double the buffer size if it is full
            std::unique_ptr<char[]> temp_output(new char[buffer_size]);
            std::memcpy(temp_output.get(), output.get(), total_read);
            output.swap(temp_output);
        }
    }

    output[total_read] = '\0';  // Null-terminate the string

    // Close the pipe
    fclose(fp);

    return std::string(output.get());  // Caller is responsible for handling the output
}

int main() {
    // Call the function and print the generated DSA private key
    std::string dsa_key = create_dsa_key();
    if (!dsa_key.empty()) {
        std::cout << dsa_key;
    } else {
        std::cerr << "Failed to generate DSA key\n";
    }

    return 0;
}
